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

### AR Game (3D)