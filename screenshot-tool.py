import pyautogui
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw
import os
from datetime import datetime
from time import sleep
import re


class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Tool")

        self.file_path = None
        self.desktop_path = None
        self.img = None
        self.img_copy = None
        self.timestamp = None
        self.pixelate_mode = False
        self.zuschneiden_mode = False
        self.screenshot_in_gui = False
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.current_line = None
        self.chosen_color = None
        self.line_width = None
        self.paint_mode = False

        # Set up the UI components
        self.setup_menu()
        self.setup_status_bar()
        self.setup_canvas()
        self.bind_mouse_events()

        # Take an initial screenshot when the app starts
        self.take_screenshot()

    def setup_menu(self):
        # Create the menu bar
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        # File Menu
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Take a screenshot", command=self.take_screenshot)
        file_menu.add_separator()
        file_menu.add_command(label="Open ...", command=self.open_image_file)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_command(label="Rename ...", command=self.rename_file)
        file_menu.add_command(label="Save as ...", command=self.save_image_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_program)

        # Edit Menu
        edit_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cropping", command=self.enable_zuschneiden_mode)
        edit_menu.add_command(label="Pixelation", command=self.enable_pixelate_mode)
        edit_menu.add_command(label="Draw Line", command=self.enable_paint_mode)

    def setup_status_bar(self):
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_canvas(self):
        # Canvas for displaying the image
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def bind_mouse_events(self):
        # Bind mouse events for selection and drawing
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def take_screenshot(self):
        self.hide_window()
        if self.screenshot_in_gui:
            sleep(1)

        screenshot = pyautogui.screenshot()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        self.file_path = os.path.join(self.desktop_path, f"screenshot_{self.timestamp}.png")

        screenshot.save(self.file_path)
        self.img = Image.open(self.file_path)
        self.img_copy = self.img.copy()

        self.open_image(self.file_path)
        self.show_window()
        self.root.state('zoomed')
        self.screenshot_in_gui = True

    def save_image(self):
        if self.img_copy and self.file_path:
            self.img_copy.save(self.file_path)
            self.update_status(f"Image saved! File name: {self.file_path}")
        else:
            messagebox.showwarning("Error", "No image loaded to save.")

    def save_image_as(self):
        if self.img_copy:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                     initialfile=f"screenshot_{self.timestamp}", 
                                                     filetypes=[("PNG files", "*.png"), 
                                                                ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
            if save_path:
                self.img_copy.save(save_path)
                self.update_status(f"Image saved! File name: {save_path}")
                self.file_path = save_path
        else:
            messagebox.showwarning("Warning", "No image loaded to save.")

    def is_valid_filename(self, filename):
        invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
        reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "LPT1", "LPT2", "LPT3"]
        
        if re.search(invalid_chars, filename):
            return False
        if filename.upper() in reserved_names or filename.endswith(' ') or filename.endswith('.'):
            return False
        return len(filename.strip()) > 0

    def rename_file(self):
        old_name = self.file_path
        new_name = simpledialog.askstring("Input", "New file name?", parent=self.root)

        if not new_name:
            messagebox.showwarning("Error", "No name entered.")
        elif not self.is_valid_filename(new_name):
            messagebox.showwarning("Error", "The file name you entered is invalid.")
        else:
            new_name = os.path.join(self.desktop_path, f"{new_name}.png")
            os.rename(old_name, new_name)
            self.file_path = new_name
            self.update_status(f"Success. New name: {new_name}")

    def open_image(self, file_path):
        self.img = Image.open(file_path)
        self.img_copy = self.img.copy()
        self.photo = ImageTk.PhotoImage(self.img_copy)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def open_image_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.bmp;*.gif")])
        if file_path:
            self.file_path = file_path
            self.img = Image.open(self.file_path)
            self.img_copy = self.img.copy()
            self.open_image(self.file_path)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose line color")
        return color_code[1]

    def get_line_size(self):
        if not self.line_width:
            self.line_width = 5
        size = simpledialog.askinteger("Input", "Enter line width:", minvalue=1, maxvalue=20, initialvalue=self.line_width)
        return size

    def pixelate_area(self, x0, y0, x1, y1):
        cropped_area = self.img_copy.crop((x0, y0, x1, y1))
        pixelated_area = cropped_area.resize((10, 10), resample=Image.NEAREST).resize(cropped_area.size, Image.NEAREST)
        self.img_copy.paste(pixelated_area, (x0, y0, x1, y1))
        self.update_canvas()

    def crop_image(self):
        if all([self.start_x, self.start_y, self.end_x, self.end_y]):
            self.img_copy = self.img_copy.crop((self.start_x, self.start_y, self.end_x, self.end_y))
            self.update_canvas()

    def enable_pixelate_mode(self):
        self.pixelate_mode = True
        self.zuschneiden_mode = False
        self.paint_mode = False
        self.update_status("Pixelation mode is activated. Select an area with the mouse.")

    def enable_zuschneiden_mode(self):
        self.pixelate_mode = False
        self.zuschneiden_mode = True
        self.paint_mode = False
        self.update_status("Cropping mode is activated. Select an area with the mouse.")

    def enable_paint_mode(self):
        self.paint_mode = True
        self.pixelate_mode = False
        self.zuschneiden_mode = False
        self.chosen_color = self.choose_color()
        self.line_width = self.get_line_size()
        self.update_status("Paint mode is activated. Draw on the canvas with the mouse.")

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.paint_mode:
            self.current_line = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill=self.chosen_color, width=self.line_width)

    def on_mouse_drag(self, event):
        if self.paint_mode:
            self.canvas.coords(self.current_line, self.start_x, self.start_y, event.x, event.y)

    def on_mouse_up(self, event):
        self.end_x = event.x
        self.end_y = event.y
        if self.paint_mode:
            draw = ImageDraw.Draw(self.img_copy)
            draw.line([(self.start_x, self.start_y), (event.x, event.y)], fill=self.chosen_color, width=self.line_width)
            self.update_canvas()
        elif self.pixelate_mode:
            self.pixelate_area(self.start_x, self.start_y, self.end_x, self.end_y)
        elif self.zuschneiden_mode:
            self.crop_image()

    def update_canvas(self):
        self.photo = ImageTk.PhotoImage(self.img_copy)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def update_status(self, new_status):
        self.status_var.set(new_status)

    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        self.root.deiconify()

    def exit_program(self):
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
