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

features:
- Marker Extrapolation (4th marker is estimated if only 3 markers are visible)
- Marker Caching (Saves marker positions for a short duration to smooth gameplay when marker visibility drops briefly)
- Contour based fingertip detection
    - backgroundsubstractor calculates contours on 2 seconds of history
    - countour with the highest y position is selected
    - highest and lowest point of the countour are calculated
    - fingertip position is at the highest point
    - fingertip rotation is based on vector from lowest to highest point

Asset Sources: 
- https://catdev-pixelarts.itch.io/catdevs-exotics-swords
- https://jennpixel.itch.io/fruits-pack-12

TODO: Write disclaimer about webcam performance (direct webcam resulted in ~3fps, obs virtual cam stable 60fps)

### AR Game (3D)