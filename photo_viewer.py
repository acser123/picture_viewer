import os
import platform
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ExifTags


class PhotoViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo Viewer (Tkinter)")
        self.geometry("1000x600")
        self.fullscreen = False  # Track fullscreen state

        # Split into left (tree) and right (image)
        self.pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.pane.pack(fill=tk.BOTH, expand=True)

        # Treeview for drives/folders/files
        self.tree = ttk.Treeview(self.pane)
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.pane.add(self.tree, weight=1)

        # Image frame (right side)
        self.image_frame = ttk.Frame(self.pane)
        self.img_label = tk.Label(
            self.image_frame, text="Select an image from the left", anchor="center"
        )
        self.img_label.pack(fill=tk.BOTH, expand=True)
        self.pane.add(self.image_frame, weight=4)

        # State
        self.current_folder = None
        self.image_files = []
        self.current_index = -1
        self.tk_image = None
        self.current_path = None
        self.exif_window = None
        self.exif_text_area = None

        # Keyboard navigation
        self.bind_all("<Key>", self._on_key)
        self.bind_all("<Alt-Return>", self.toggle_fullscreen)

        # Resize handler
        self.image_frame.bind("<Configure>", self._on_resize)

        # Populate root drives and select first item
        self.populate_roots()

    def populate_roots(self):
        if platform.system() == "Windows":
            import string
            drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            for d in drives:
                node = self.tree.insert("", "end", text=d, values=[d])
                self.tree.insert(node, "end")  # dummy child
        else:
            node = self.tree.insert("", "end", text="/", values=["/"])
            self.tree.insert(node, "end")  # dummy child

        # Automatically select the first root item and give Treeview focus
        first = self.tree.get_children("")
        if first:
            self.tree.selection_set(first[0])
            self.tree.focus(first[0])
            self.tree.see(first[0])
            self.tree.focus_set()
            self.open_selected()

    def on_open_node(self, event):
        node = self.tree.focus()
        values = self.tree.item(node, "values")
        if not values:
            return
        path = values[0]
        self.tree.delete(*self.tree.get_children(node))

        try:
            for name in sorted(os.listdir(path), key=lambda s: s.lower()):
                abspath = os.path.join(path, name)
                if os.path.isdir(abspath):
                    new_node = self.tree.insert(node, "end", text=name, values=[abspath])
                    self.tree.insert(new_node, "end")  # dummy child
                else:
                    self.tree.insert(node, "end", text=name, values=[abspath])
        except (PermissionError, FileNotFoundError):
            pass

    def on_double_click(self, event):
        self.open_selected()

    def open_selected(self):
        node = self.tree.focus()
        values = self.tree.item(node, "values")
        if not values:
            return
        file_path = values[0]
        if os.path.isfile(file_path):
            folder = os.path.dirname(file_path)
            try:
                files = [
                    f
                    for f in os.listdir(folder)
                    if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif"))
                ]
            except PermissionError:
                files = []
            files.sort()
            if files:
                self.current_folder = folder
                self.image_files = files
                basename = os.path.basename(file_path)
                if basename in self.image_files:
                    self.current_index = self.image_files.index(basename)
                else:
                    self.current_index = 0
                self.show_image(file_path)

    def show_image(self, file_path):
        try:
            img = Image.open(file_path)
            w = max(50, self.img_label.winfo_width())
            h = max(50, self.img_label.winfo_height())
            if w < 100 or h < 100:
                w = max(w, int(self.winfo_width() * 0.6) or 800)
                h = max(h, int(self.winfo_height() * 0.8) or 600)
            img.thumbnail((w, h), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.tk_image, text="")
            self.current_path = file_path

            # Update EXIF window if it exists
            if self.exif_window and self.exif_window.winfo_exists():
                self.update_exif_window()
        except Exception as e:
            self.img_label.config(text=f"Error loading image:\n{e}", image="")
            self.tk_image = None
            self.current_path = None

    def _on_key(self, event):
        key = (event.keysym or "").lower()
        if key == "a":
            self._move_selection(-1, auto_open=True)
        elif key == "s":
            self._move_selection(1, auto_open=True)
        elif key == "up":
            self.after(1, self.open_selected)
        elif key == "down":
            self.after(1, self.open_selected)
        elif key == "return":
            self.open_selected()
        elif key == "i":
            self.toggle_exif_window()  # Toggle EXIF window

    def _move_selection(self, direction, auto_open=False):
        sel = self.tree.selection()
        if not sel:
            first = self.tree.get_children("")
            if first:
                self.tree.selection_set(first[0])
                self.tree.focus(first[0])
                self.tree.see(first[0])
                if auto_open:
                    self.open_selected()
            return
        cur = sel[0]
        parent = self.tree.parent(cur)
        siblings = list(self.tree.get_children(parent))
        if cur in siblings:
            idx = siblings.index(cur)
            new_idx = idx + direction
            if 0 <= new_idx < len(siblings):
                new_item = siblings[new_idx]
                self.tree.selection_set(new_item)
                self.tree.focus(new_item)
                self.tree.see(new_item)
                if auto_open:
                    self.open_selected()

    def _on_resize(self, event):
        if self.current_path:
            self.show_image(self.current_path)

    # ------------------- EXIF window functionality -------------------
    def toggle_exif_window(self):
        """Show or hide the EXIF window."""
        if self.exif_window and self.exif_window.winfo_exists():
            self.exif_window.destroy()
            self.exif_window = None
            self.exif_text_area = None
        else:
            self.show_exif_window()

    def show_exif_window(self):
        if not self.current_path:
            messagebox.showinfo("EXIF Info", "No image loaded.")
            return

        # Create EXIF window if it doesn't exist
        if not self.exif_window or not self.exif_window.winfo_exists():
            self.exif_window = tk.Toplevel(self)
            self.exif_window.title(f"EXIF Data for {os.path.basename(self.current_path)}")
            self.exif_window.geometry("600x400")
            self.exif_window.protocol("WM_DELETE_WINDOW", self.exif_window.destroy)

            # Scrollable text widget
            self.exif_text_area = tk.Text(self.exif_window, wrap="word", height=20, width=80)
            scrollbar = tk.Scrollbar(self.exif_window, command=self.exif_text_area.yview)
            self.exif_text_area.config(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            self.exif_text_area.pack(side="left", fill="both", expand=True)

        self.update_exif_window()

    def update_exif_window(self):
        if not self.current_path or not self.exif_text_area:
            return
        try:
            img = Image.open(self.current_path)
            exif_data = img._getexif()

            self.exif_text_area.config(state="normal")
            self.exif_text_area.delete(1.0, tk.END)

            if not exif_data:
                self.exif_text_area.insert(tk.END, "No EXIF data found for this image.")
            else:
                decoded_exif = {
                    ExifTags.TAGS.get(tag_id, tag_id): value
                    for tag_id, value in exif_data.items()
                }

                # Handle GPSInfo separately
                if "GPSInfo" in decoded_exif and isinstance(decoded_exif["GPSInfo"], dict):
                    gps_info = decoded_exif["GPSInfo"]
                    decoded_gps = {
                        ExifTags.GPSTAGS.get(tag, tag): val for tag, val in gps_info.items()
                    }
                    decoded_exif["GPSInfo"] = decoded_gps

                for tag, value in decoded_exif.items():
                    if isinstance(value, dict):
                        self.exif_text_area.insert(tk.END, f"{tag}:\n")
                        for sub_tag, sub_val in value.items():
                            self.exif_text_area.insert(tk.END, f"  {sub_tag}: {sub_val}\n")
                    else:
                        self.exif_text_area.insert(tk.END, f"{tag}: {value}\n")

            self.exif_text_area.config(state="disabled")

        except Exception as e:
            self.exif_text_area.config(state="normal")
            self.exif_text_area.delete(1.0, tk.END)
            self.exif_text_area.insert(tk.END, f"Error reading EXIF: {e}")
            self.exif_text_area.config(state="disabled")

    # ------------------- Fullscreen toggle -------------------
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode."""
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)


if __name__ == "__main__":
    app = PhotoViewer()
    app.mainloop()
