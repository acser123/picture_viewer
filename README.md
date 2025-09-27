# Photo Viewer

A simple GUI-based photo viewer built with Python and Tkinter.

## Features

- **Synchronized File Directory Panel**: The left panel displays the contents of the currently viewed image's directory, keeping the file list in sync with the displayed image.
- **Image Viewing**: Open and display images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`).
- **Seamless Navigation**: Cycle through images in the same directory using "Next" and "Previous" buttons, with the file panel automatically highlighting the current image.
- **Intuitive Interface**: Simple and easy-to-use GUI.

## Prerequisites

- Python 3.x
- Pip (Python package installer)

## Installation

1.  **Clone the repository or download the source code.**

2.  **Navigate to the project directory:**
    ```bash
    cd path/to/photo-viewer
    ```

3.  **Install the required dependencies:**
    This application uses the Pillow library to handle images. You can install it using pip:
    ```bash
    pip install Pillow
    ```

## Usage

To run the application, execute the following command in your terminal:
```bash
python photo_viewer.py
```

This will open the photo viewer window.

-   **Opening an Image**: Click the "Open Image" button to select an image. The directory containing that image will be displayed in the left-hand panel, with the selected image highlighted.
-   **Navigating**: Use the "Next" and "Previous" buttons to cycle through images in the current directory. The selection in the file panel will update automatically. You can also click on another image in the panel to view it, or click a directory to navigate to it.