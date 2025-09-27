# Photo Viewer

A GUI-based photo viewer application built with Python and Tkinter.

## Features

- **Drive and Folder Navigation**: The left panel provides a tree view to navigate your computer's drives and folders.
- **Image Display**: Click on an image file in the navigation panel to display it in the main viewer on the right.
- **Keyboard Navigation**: Once an image is displayed, use the **Left Arrow** and **Right Arrow** keys to cycle through other images in the same folder.
- **Synchronized View**: The selection in the navigation panel stays in sync with the image being viewed, automatically highlighting the current file.

## Prerequisites

- Python 3.x
- Pillow library

## Installation

1.  **Clone or download the source code.**

2.  **Install the required dependencies:**
    This application uses the Pillow library to handle images. You can install it using pip:
    ```bash
    pip install Pillow
    ```

## Usage

To run the application, execute the following command in your terminal:
```bash
python photo_viewer.py
```

- **Browse**: Use the left panel to navigate to a folder containing images.
- **View**: Click on an image file to display it.
- **Navigate**: Use the arrow keys to move to the next or previous image.