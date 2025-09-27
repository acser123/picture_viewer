import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

class PhotoViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Viewer")
        self.root.geometry("800x600")

        self.image_path = None
        self.image_list = []
        self.current_image_index = -1

        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        self.lbl_image = tk.Label(self.frame)
        self.lbl_image.pack(pady=10, fill="both", expand=True)

        self.btn_frame = tk.Frame(self.frame)
        self.btn_frame.pack(pady=5)

        self.btn_prev = tk.Button(self.btn_frame, text="Previous", command=self.prev_image)
        self.btn_prev.pack(side="left", padx=5)

        self.btn_open = tk.Button(self.btn_frame, text="Open Image", command=self.open_image)
        self.btn_open.pack(side="left", padx=5)

        self.btn_next = tk.Button(self.btn_frame, text="Next", command=self.next_image)
        self.btn_next.pack(side="left", padx=5)

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if path:
            directory = os.path.dirname(path)
            self.image_list = [
                os.path.join(directory, f) for f in os.listdir(directory)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
            ]
            try:
                self.current_image_index = self.image_list.index(path)
                self.load_image(path)
            except ValueError:
                self.load_image(path) # Fallback for case-sensitivity issues

    def load_image(self, path):
        self.image_path = path
        try:
            img = Image.open(path)
            img.thumbnail((self.frame.winfo_width() - 20, self.frame.winfo_height() - 60))
            photo = ImageTk.PhotoImage(img)
            self.lbl_image.config(image=photo)
            self.lbl_image.image = photo
        except Exception as e:
            print(f"Error opening image: {e}")

    def next_image(self):
        if self.image_list:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
            self.load_image(self.image_list[self.current_image_index])

    def prev_image(self):
        if self.image_list:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_list)
            self.load_image(self.image_list[self.current_image_index])

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoViewer(root)
    root.mainloop()