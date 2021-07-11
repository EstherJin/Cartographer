# Cartographer
Makes Frigid Mapeys

### Controls
Right Click - Erase everything off that one tile (doesn't support right click and hold, if you want that, use the regular eraser)
'e' key - Toggles enemy spawner
'z' key - Undos (doesn't undo wall decorations or enemy toggle yet)

### Uploading Pictures
First, find the directory your images belong to (obstacles, walls, hang etc.)

Image names follow the following format: <Number>-<Name>_<(Tuple of Coordinates).png (e.g. '2-Pillar_(-1,-61)')

How the coordinates work:
For obstacles and floor things, the top right corner of the image is naturally centered to top right corner of the tile. (for the hangys, the bottom right corner of the image is naturally centered to bottom right corner of the tile). (0,0) coordinates won't move the image from the natural position. (1,2) will shift the image right by 1 pixel and down by 2 pixels. (-1,-2) will shift the image left by 1 pixel and up by 2 pixels.
