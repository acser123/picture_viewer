import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

class PhotoViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Viewer")
        self.root.geometry("1024x600")

        self.image_path = None
        self.image_list = []
        self.current_image_index = -1

        # Create a PanedWindow for resizable frames
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill="both", expand=True)

        # Frame for the directory tree
        self.tree_frame = tk.Frame(self.paned_window, width=250)
        self.paned_window.add(self.tree_frame, stretch="never")

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree_scroll = tk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree_scroll.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=self.tree_scroll.set)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.populate_tree()

        # Frame for the image viewer
        self.viewer_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.viewer_frame, stretch="always")

        self.lbl_image = tk.Label(self.viewer_frame)
        self.lbl_image.pack(pady=10, fill="both", expand=True)

        self.btn_frame = tk.Frame(self.viewer_frame)
        self.btn_frame.pack(pady=5)

        self.btn_prev = tk.Button(self.btn_frame, text="Previous", command=self.prev_image)
        self.btn_prev.pack(side="left", padx=5)

        self.btn_open = tk.Button(self.btn_frame, text="Open Image", command=self.open_image)
        self.btn_open.pack(side="left", padx=5)

        self.btn_next = tk.Button(self.btn_frame, text="Next", command=self.next_image)
        self.btn_next.pack(side="left", padx=5)

    def populate_tree(self):
        home_dir = os.path.expanduser("~")
        self.insert_node("", home_dir, home_dir)

    def insert_node(self, parent, path, text):
        node = self.tree.insert(parent, "end", text=text, values=[path], open=False)
        if os.path.isdir(path):
            self.tree.insert(node, "end", text="dummy") # Add a dummy item

    def on_tree_open(self, event):
        item = self.tree.focus()
        path = self.tree.item(item, "values")[0]
        if os.path.isdir(path):
            # Clear dummy node
            children = self.tree.get_children(item)
            self.tree.delete(*children)

            try:
                for p in os.listdir(path):
                    full_path = os.path.join(path, p)
                    if os.path.isdir(full_path):
                        self.insert_node(item, full_path, p)
                    elif p.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                        self.insert_node(item, full_path, p)
            except OSError:
                pass # Ignore permission errors

    def on_tree_select(self, event):
        item = self.tree.focus()
        path = self.tree.item(item, "values")[0]
        if os.path.isfile(path):
            directory = os.path.dirname(path)
            self.image_list = [
                os.path.join(directory, f) for f in os.listdir(directory)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
            ]
            try:
                self.current_image_index = self.image_list.index(path)
                self.load_image(path)
            except (ValueError, IndexError):
                self.load_image(path)

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
            img.thumbnail((self.viewer_frame.winfo_width() - 20, self.viewer_frame.winfo_height() - 60))
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