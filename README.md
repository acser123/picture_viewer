# Photo Viewer

A simple GUI-based photo viewer built with Python and Tkinter.

## Features

- **File Directory Panel**: Browse your file system with a resizable directory tree.
- **Image Viewing**: Open and display images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`).
- **Navigation**: Cycle through images in the same directory using "Next" and "Previous" buttons.
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

This will open the photo viewer window, which is split into two main sections:
-   **File Directory Panel (Left)**: Use the tree view to navigate through your directories. Click on a directory to expand it and see its subdirectories and image files.
-   **Image Viewer (Right)**: Click on an image file in the directory panel to display it here.

Once an image is loaded, you can use the "Next" and "Previous" buttons to browse other images in the same directory. You can also use the "Open Image" button to open an image using the system's file dialog.