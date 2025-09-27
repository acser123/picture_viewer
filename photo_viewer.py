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
        self.current_directory = None

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
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

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

    def populate_tree_for_directory(self, directory):
        self.tree.delete(*self.tree.get_children())
        self.current_directory = directory

        parent_dir = os.path.dirname(directory)
        self.tree.insert("", "end", text="..", values=[parent_dir], open=False)

        try:
            for item in sorted(os.listdir(directory)):
                path = os.path.join(directory, item)
                if os.path.isdir(path):
                    self.tree.insert("", "end", text=f"[{item}]", values=[path], open=False)
                elif item.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                    self.tree.insert("", "end", text=item, values=[path], open=False)
        except OSError:
            pass

    def on_tree_select(self, event):
        if not self.tree.selection():
            return
        item = self.tree.selection()[0]
        path = self.tree.item(item, "values")[0]

        if os.path.isdir(path):
            self.populate_tree_for_directory(path)
        elif os.path.isfile(path) and path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            self.load_image(path)

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if path:
            self.load_image(path)

    def load_image(self, path):
        directory = os.path.dirname(path)
        if directory != self.current_directory:
            self.populate_tree_for_directory(directory)

        self.image_path = path
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
            img.thumbnail((self.viewer_frame.winfo_width() - 20, self.viewer_frame.winfo_height() - 60))
            photo = ImageTk.PhotoImage(img)
            self.lbl_image.config(image=photo)
            self.lbl_image.image = photo
        except Exception as e:
            print(f"Error opening image: {e}")

        # Synchronize tree selection
        self.tree.unbind("<<TreeviewSelect>>")
        try:
            for item in self.tree.get_children(""):
                if self.tree.item(item, "values")[0] == self.image_path:
                    self.tree.selection_set(item)
                    self.tree.focus(item)
                    self.tree.see(item)
                    break
        finally:
            self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def next_image(self):
        if not self.image_list:
            return
        self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
        self.load_image(self.image_list[self.current_image_index])

    def prev_image(self):
        if not self.image_list:
            return
        self.current_image_index = (self.current_image_index - 1 + len(self.image_list)) % len(self.image_list)
        self.load_image(self.image_list[self.current_image_index])

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoViewer(root)
    root.mainloop()