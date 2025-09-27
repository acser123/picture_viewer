import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class PhotoViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Viewer")
        self.root.geometry("1024x768")

        self.image_path = None
        self.image_list = []
        self.current_image_index = -1

        # Create a PanedWindow for resizable frames
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill="both", expand=True)

        # Frame for the directory tree
        self.tree_frame = tk.Frame(self.paned_window, width=300)
        self.paned_window.add(self.tree_frame, stretch="never")

        self.tree = ttk.Treeview(self.tree_frame)
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree_scroll = tk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree_scroll.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=self.tree_scroll.set)

        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.populate_drives()

        # Frame for the image viewer
        self.viewer_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.viewer_frame, stretch="always")

        # Add a label for the image
        self.lbl_image = tk.Label(self.viewer_frame)
        self.lbl_image.pack(fill="both", expand=True)

        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)

    def next_image(self, event=None):
        if not self.image_list:
            return
        self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
        self.load_image(self.image_list[self.current_image_index])

    def prev_image(self, event=None):
        if not self.image_list:
            return
        self.current_image_index = (self.current_image_index - 1 + len(self.image_list)) % len(self.image_list)
        self.load_image(self.image_list[self.current_image_index])

    def populate_drives(self):
        if os.name == "nt":
            drives = [f"{chr(drive)}:\\" for drive in range(65, 91) if os.path.exists(f"{chr(drive)}:\\")]
            for drive in drives:
                self.insert_node("", drive, drive)
        else:
            self.insert_node("", "/", "/")

    def insert_node(self, parent, path, text):
        node = self.tree.insert(parent, "end", text=text, values=[path], open=False)
        if os.path.isdir(path):
            self.tree.insert(node, "end", text="dummy")

    def on_tree_open(self, event):
        item = self.tree.focus()
        path = self.tree.item(item, "values")[0]

        # Clear dummy node
        children = self.tree.get_children(item)
        self.tree.delete(*children)

        try:
            for p in sorted(os.listdir(path), key=str.lower):
                full_path = os.path.join(path, p)
                if os.path.isdir(full_path):
                    self.insert_node(item, full_path, p)
                elif p.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                    self.insert_node(item, full_path, p)
        except OSError:
            pass # Ignore permission errors

    def on_tree_select(self, event):
        if not self.tree.selection():
            return
        item = self.tree.selection()[0]
        path = self.tree.item(item, "values")[0]

        if os.path.isfile(path) and path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            self.load_image(path)

    def load_image(self, path):
        self.image_path = path
        directory = os.path.dirname(path)

        self.image_list = sorted([
            os.path.join(directory, f) for f in os.listdir(directory)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
        ])
        try:
            self.current_image_index = self.image_list.index(path)
        except ValueError:
            self.image_list.append(path)
            self.current_image_index = len(self.image_list) - 1

        try:
            img = Image.open(path)
            w, h = self.viewer_frame.winfo_width(), self.viewer_frame.winfo_height()
            if w < 2 or h < 2: # Fallback if frame size is not yet determined
                w, h = 700, 700
            img.thumbnail((w - 20, h - 20))
            photo = ImageTk.PhotoImage(img)
            self.lbl_image.config(image=photo)
            self.lbl_image.image = photo
        except Exception as e:
            print(f"Error loading image: {e}")

        # Synchronize tree selection
        parent_item = self.tree.parent(self.tree.focus())
        if parent_item:
            self.tree.unbind("<<TreeviewSelect>>")
            try:
                for item in self.tree.get_children(parent_item):
                    if self.tree.item(item, "values")[0] == self.image_path:
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        self.tree.see(item)
                        break
            finally:
                self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoViewer(root)
    root.mainloop()