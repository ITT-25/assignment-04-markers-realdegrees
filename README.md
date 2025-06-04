[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/-leASaOw)

# Setup

1. Clone the repo
2. `cd` into the root folder
3. Setup a virtual env
4. `pip install -r requirements.txt`

# Perspective Transformation


```sh
cd perspective_transformation
python image_extractor.py -i sample_image.jpg -o sample_image_transformed.jpg
```
> 💡 Use `python image_extractor.py --help` to list all CLI params including width and height

Opens a GUI displaying the input image.  
`Left Click` to add a point. When 4 points (forming a valid quad) are added a new GUI with the transformed image pops up.  
Controls are displayed in the window title. Console logs give further info about point selection etc.

### AR Game

The game I created for this assignment is a fruit ninja clone (Frucht NinjAR 🧠) that allows the player to control a sword to slash fruit and avoid bombs by moving their hand between the webcam and the board.

```sh
cd ar_game
python AR_game.py --video-id 0 --width 1920 --height 1080
```

This launches the game, for more CLI options use the `--help` flag.  
It is recommended to stay on the default resolution (1920x1080)*(I did not make gravity and drag responsive so gameplay might be off at vastly different resolutions)*.  
If you do not immediately see your webcam feed in the app, adjust the `--video-id` param.  
If the program does not detect any markers on the board, your webcam is likely mirrored.    

> ⚠️ PERFORMANCE: Using my default webcam resulted in ~3 FPS. OBS Virtual Cam (using the same webcam) results in steady 60+ FPS.
If you get unreasonably bad performance try a different setup or a virtual camera.

> ⚠️ LIGHTING: The game works very good in low light conditions due to the marker caching, marker interpolation and robust fingertip detection, however it is recommended to have decent lighting conditions
If the game doesn't work as expected you can adjust the `--sensitivity` (Lower for bright environments e.g. 15, Higher for dark environments e.g. 70+)
This might also depend on the webcam so if you don't get proper tracking play around with the sensitivity using the `--debug` flag until the sword follows your fingertip correctly during gameplay. I got vastly different results on my laptop vs pc.

> 💡 The game will automatically select the lowest resolution supported by your webcam (for performance reasons) and match it up with the window size, most webcams should be compatible (maybe not vertical ones).
If the webcam image in the game window is slightly stretched it can be ignored as long as the aruco markers are detected correctly. 

#### Technical Features

- Marker Extrapolation
    - 4th marker is estimated if only 3 markers are visible
    - Allows players to completely cover one of the markers with their arm during gameplay without interruption
- Marker Caching 
    - Saves marker positions for a short duration to smooth gameplay when marker visibility drops briefly
    - Results in uninterrupted gameplay when one or multiple markers disappear
- Contour based fingertip detection
    - Countour with the highest y position is selected
    - Highest and lowest point of the countour are calculated
    - Fingertip position is at the highest point
    - Fingertip rotation is based on vector from lowest to highest point
    - Use the `--debug` flag to see this visualized
- Auto Pause
    - The game pauses and resumes when losing or gaining vision of the board

#### Gameplay Instructions

Launch the game and bring your game board into view. Once the board is detected a timer will count down on the screen.  
When the timer is done the game starts throwing fruits and bombs towards the center from the sides.
Move a finger or hand in front of the game board, a sword will appear at the tip if your finger! Use this sword to slash as many fruits as you can while avoiding the bombs!

<img src="doc/gameplay.gif" width="35%" alt="Game over demonstration">


Each bomb **reduces** your points by `30 points`!  
Each fruit **increases** your points by `10 points`!  
Missing a fruit will **reduce** your points by `5 points`!  

The points required to reach the next level scale up with each level as well as the amount of fruit and bombs, see how high you can get!   
When point reductions reduce your points below `0 points` the `negative point bar` will show up at the top. When this bar reaches `-100 points` you lose all your progress and have to start from level 0.

<img src="doc/game_over.gif" width="35%" alt="Game over demonstration">

### AR Game (3D)

A simple extension of the sample app. Marker IDs 4 and 5 are mapped to [enton.obj](ar_game_3d/enton.obj) and [glurak.obj](ar_game_3d/glurak.obj).  
When the markers are within a certain distance of each other, the characters will start attacking each other. They use the default scaling animation to attack.  
The first character that drops to 0 health shrinks and disappears.

```sh
cd ar_game
python AR_game_3d.py
```

**Known Issues**
- No matter which model I tried or how I exported them from blender I couldn't get the model to have textures.  
- The models often invert their rotation briefly, likely due to the way marker position and rotation are calculated.  
- Rotation on the local up axis didn't work so I couldn't get the models to turn towards each other, probably due to them being rotated differently in the model itself and the sample logic doesn't account for that

## Sources

All assets used are free to use, modify and distribute non-commercially.

Asset Sources: 
- https://catdev-pixelarts.itch.io/catdevs-exotics-swords (Sword)
- https://jennpixel.itch.io/fruits-pack-12 (Fruits)
- https://ahninniah.itch.io/free-game-items-pack-2 (Bomb)
- https://www.cgtrader.com/free-3d-models/animals/reptile/animated-charizard-pokemon-3d-model (3D Model)
