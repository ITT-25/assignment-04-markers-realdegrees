import cv2
import cv2.aruco as aruco
import numpy as np
import pyglet
import math

from pyglet.gl import GL_DEPTH_TEST, GL_CULL_FACE, glEnable
from pyglet.math import Mat4, Vec3

from AR_model import Model
from character import Character
from game_manager import GameManager
from utils import cv2glet, estimatePoseMarker, get_center_of_marker
from config import (
    INVERSE_MATRIX, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_Z,
    CAMERA_MATRIX, DIST_COEFFS
)


# Setup window and OpenGL
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, resizable=False, caption="3D AR Character Battle")

# Setup camera
cap = cv2.VideoCapture(2)

# Setup ArUco detector
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
aruco_params = aruco.DetectorParameters()
detector = aruco.ArucoDetector(aruco_dict, aruco_params)

# Game manager
game_manager = GameManager()


@window.event
def on_draw():
    global view_matrix, position
    
    # Capture frame
    ret, frame = cap.read()
    if not ret:
        return
        
    # Convert to grayscale for marker detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect ArUco markers
    corners, ids, _ = detector.detectMarkers(gray)
    
    # Draw detected markers
    if corners:
        aruco.drawDetectedMarkers(frame, corners)    # Process detected markers
    if ids is not None:
        for i, marker_id in enumerate(ids):
            marker_id = int(marker_id[0])
            position = get_center_of_marker(corners[i][0])
            rvec, tvec, marker_length = estimatePoseMarker(corners[i], CAMERA_MATRIX, DIST_COEFFS)
            
            # Convert rotation vector to matrix for OpenGL
            rmtx = cv2.Rodrigues(rvec[0])[0]
            view_matrix = np.array([
                [rmtx[0][0], rmtx[0][1], rmtx[0][2], tvec[0,0,0]],
                [rmtx[1][0], rmtx[1][1], rmtx[1][2], tvec[0,0,1]],
                [rmtx[2][0], rmtx[2][1], rmtx[2][2], tvec[0,0,2]],
                [0.0, 0.0, 0.0, 1.0]
            ], dtype="object")
            view_matrix = view_matrix * INVERSE_MATRIX
            view_matrix = np.transpose(view_matrix)
            
            # Update character models with current marker data
            for character in game_manager.characters:
                if character.character_id == marker_id:
                    character.update_marker_data(view_matrix, position, marker_length)
    
    # Update game manager first to handle character states and visibility
    game_manager.update(1/60)
    
    # Update all characters and handle model positioning (using cached or current data)
    for character in game_manager.characters:
        view_matrix, position, marker_length = character.get_current_marker_data()
        
        if character.is_visible and view_matrix is not None:
            character.model.setup_translation(character.character_id, view_matrix, position, marker_length)
            
            # Add attack animation effects
            if character.is_attacking:
                # Scale up the character during attack
                character.model._scaling_factor = 0.25 + 0.05 * math.sin(character.attack_animation_time * 10)
      # Convert frame to pyglet format
    img = cv2glet(frame, 'BGR')
    
    # Clear and draw
    window.clear()
    img.blit(-WINDOW_WIDTH/2, -WINDOW_HEIGHT/2, 0)
    
    # Draw 3D models
    for character in game_manager.characters:
        if character.is_visible:
            character.model.batch.draw()
    


def animate(dt):
    """Animation update function"""
    for character in game_manager.characters:
        if character.is_visible:
            character.model.animate()


@window.event
def on_resize(width, height):
    """Handle window resize"""
    window.viewport = (0, 0, width, height)
    window.projection = Mat4.perspective_projection(window.aspect_ratio, z_near=0.1, z_far=1024)
    return pyglet.event.EVENT_HANDLED


@window.event
def on_close():
    """Clean up when closing"""
    cap.release()
    cv2.destroyAllWindows()


def main():
    """Main function to start the AR game"""
    # Enable OpenGL features
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    
    # Create character models
    character1_model = Model(
        path="enton.obj", 
        id=4, 
        win_w=WINDOW_WIDTH, 
        win_h=WINDOW_HEIGHT, 
        rot_x=270, 
        rot_y=90, 
        rot_z=270, 
        scaling_factor=0.2
    )
    
    character2_model = Model(
        path="glurak.obj", 
        id=5, 
        win_w=WINDOW_WIDTH, 
        win_h=WINDOW_HEIGHT, 
        rot_x=90, 
        rot_y=90, 
        rot_z=0, 
        scaling_factor=0.2
    )
    
    # Create characters
    character1 = Character(character1_model, 4, "Enton")
    character2 = Character(character2_model, 5, "Glurak")

    # Add characters to game manager
    game_manager.add_character(character1)
    game_manager.add_character(character2)
    
    # Setup camera view
    window.view = Mat4.look_at(
        position=Vec3(0, 0, WINDOW_Z), 
        target=Vec3(0, 0, 0), 
        up=Vec3(0, 1, 0)
    )
    window.viewport = (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    window.projection = Mat4.perspective_projection(window.aspect_ratio, z_near=0.1, z_far=1024)
    
    # Start animation loop
    pyglet.clock.schedule_interval(animate, 1 / 60)
    
    print("3D AR Game Started!")
    print("Instructions:")
    print("- Show ArUco markers with IDs 4 and 5")
    print("- Characters will appear on their respective markers")
    print("- When markers are close enough, characters will fight automatically")
    
    # Start the game
    pyglet.app.run()


if __name__ == "__main__":
    main()
