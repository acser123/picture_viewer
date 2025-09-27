import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ExifTags
import os
import threading
import queue

class PhotoViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Viewer")
        self.root.geometry("1024x768")

        self.image_path = None
        self.image_list = []
        self.current_image_index = -1
        self.gui_queue = queue.Queue()
        self.request_queue = queue.Queue()
        self.exif_window = None

        # Create and start the single worker thread
        self.worker_thread = threading.Thread(target=self._worker_thread_loop, daemon=True)
        self.worker_thread.start()

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
        self.process_queue()

        # Frame for the image viewer
        self.viewer_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.viewer_frame, stretch="always")

        # Add a label for the image
        self.lbl_image = tk.Label(self.viewer_frame)
        self.lbl_image.pack(fill="both", expand=True)

        self.btn_frame = tk.Frame(self.viewer_frame)
        self.btn_frame.pack(pady=5)

        self.btn_exif = tk.Button(self.btn_frame, text="Show EXIF", command=self.show_exif_data)
        self.btn_exif.pack()

        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<i>", self.show_exif_data)

    def process_queue(self):
        try:
            while True:
                task = self.gui_queue.get_nowait()
                action, data = task
                if action == 'populate_nodes':
                    for node_data in data:
                        self.insert_node(node_data['parent'], node_data['path'], node_data['text'])
                elif action == 'update_image':
                    self._update_image_display(data)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

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

        # Put a request in the queue for the worker thread
        self.request_queue.put(('get_dir', {'path': path, 'item': item}))

    def get_directory_contents(self, path, item):
        try:
            nodes_to_add = []
            for p in sorted(os.listdir(path), key=str.lower):
                full_path = os.path.join(path, p)
                if os.path.isdir(full_path):
                    nodes_to_add.append({'parent': item, 'path': full_path, 'text': p, 'is_dir': True})
                elif p.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                    nodes_to_add.append({'parent': item, 'path': full_path, 'text': p, 'is_dir': False})
            if nodes_to_add:
                self.gui_queue.put(('populate_nodes', nodes_to_add))
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
        # Put a request in the queue for the worker thread
        self.request_queue.put(('load_img', {'path': path}))

    def _load_image_in_background(self, path):
        try:
            directory = os.path.dirname(path)

            image_list = sorted([
                os.path.join(directory, f) for f in os.listdir(directory)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
            ])

            current_image_index = image_list.index(path)

            img = Image.open(path)
            img.load() # Pre-load image data

            self.gui_queue.put(('update_image', {
                'path': path,
                'image_list': image_list,
                'current_image_index': current_image_index,
                'image_object': img
            }))
        except (ValueError, OSError, IndexError) as e:
            print(f"Error loading image in background: {e}")

    def _update_image_display(self, data):
        self.image_path = data['path']
        self.image_list = data['image_list']
        self.current_image_index = data['current_image_index']

        try:
            img = data['image_object']
            w, h = self.viewer_frame.winfo_width(), self.viewer_frame.winfo_height()
            if w < 2 or h < 2:
                w, h = 700, 700
            img.thumbnail((w - 20, h - 20))
            photo = ImageTk.PhotoImage(img)
            self.lbl_image.config(image=photo)
            self.lbl_image.image = photo
        except Exception as e:
            print(f"Error updating image display: {e}")

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

    def show_exif_data(self, event=None):
        if self.exif_window and self.exif_window.winfo_exists():
            self.exif_window.destroy()
            return

        if not self.image_path:
            tk.messagebox.showinfo("EXIF Info", "No image loaded.")
            return

        try:
            img = Image.open(self.image_path)
            exif_data = img._getexif()

            if not exif_data:
                tk.messagebox.showinfo("EXIF Info", "No EXIF data found for this image.")
                return

            self.exif_window = tk.Toplevel(self.root)
            self.exif_window.title(f"EXIF Data for {os.path.basename(self.image_path)}")
            self.exif_window.geometry("600x400")
            self.exif_window.bind("<Destroy>", self._on_exif_window_close)

            text_area = tk.Text(self.exif_window, wrap="word", height=20, width=80)
            scrollbar = tk.Scrollbar(self.exif_window, command=text_area.yview)
            text_area.config(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            text_area.pack(side="left", fill="both", expand=True)

            decoded_exif = {
                ExifTags.TAGS.get(tag_id, tag_id): value
                for tag_id, value in exif_data.items()
            }

            exif_info = ""
            for tag, value in decoded_exif.items():
                exif_info += f"{tag}: {value}\n"

            text_area.insert("1.0", exif_info)
            text_area.config(state="disabled")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Error reading EXIF data: {e}")

    def _on_exif_window_close(self, event=None):
        self.exif_window = None

    def _worker_thread_loop(self):
        while True:
            request = self.request_queue.get()
            action, data = request
            if action == 'get_dir':
                self.get_directory_contents(data['path'], data['item'])
            elif action == 'load_img':
                self._load_image_in_background(data['path'])

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoViewer(root)
    root.mainloop()