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

> ⚠️ Using my default webcam resulted in ~3 FPS. OBS Virtual Cam results in steady 60+ FPS.
If you get unreasonably bad performance try a different setup or a virtual camera.

> ⚠️ The game works very good in low light conditions due to the marker caching, marker interpolation and robust fingertip detection, however it is recommended to at least have the physical board well lit to avoid any hiccups during gameplay

> 💡 The game will automatically select the best resolution for your webcam and match it up with the window size, most webcams should be compatible (maybe not vertical ones).
If the webcam image in the game window is slightly stretched it can be ignored as long as the aruco markers are detected correctly.

#### Technical Features

- Marker Extrapolation
    - 4th marker is estimated if only 3 markers are visible
- Marker Caching 
    - Saves marker positions for a short duration to smooth gameplay when marker visibility drops briefly
- Contour based fingertip detection
    - countour with the highest y position is selected
    - highest and lowest point of the countour are calculated
    - fingertip position is at the highest point
    - fingertip rotation is based on vector from lowest to highest point
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

#### Sources

All assets used are free to use, modify and distribute.

Asset Sources: 
- https://catdev-pixelarts.itch.io/catdevs-exotics-swords (Sword)
- https://jennpixel.itch.io/fruits-pack-12 (Fruits)
- https://ahninniah.itch.io/free-game-items-pack-2 (Bomb)

### AR Game (3D)

TODO