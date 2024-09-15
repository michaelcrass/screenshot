import pyautogui
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox, filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw
import os
from datetime import datetime
from time import sleep
import re


file_path, desktop_path, img, img_copy, timestamp = None, None, None, None, None
pixelate_mode, zuschneiden_mode, screenshot_in_gui = False, False, False
start_x, start_y, end_x, end_y, current_line = None, None, None, None, None
chosen_color, line_width = None, None

# Funktion, um einen Screenshot zu machen
def take_screenshot():
    global img, img_copy, file_path,desktop_path, screenshot_in_gui,timestamp

    hide() # hide window
    if screenshot_in_gui:
        sleep(1)

    # Screenshot erstellen
    screenshot = pyautogui.screenshot()

    # Dateiname basierend auf Timestamp festlegen
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    file_path = os.path.join(desktop_path, f"screenshot_{timestamp}.png")

    # Screenshot speichern
    screenshot.save(file_path)

    # Bild öffnen und anzeigen
    img = Image.open(file_path)
    img_copy = img.copy()
    open_image(file_path)

    show() # show Window

    root.state('zoomed')  # Vollbildmodus
    screenshot_in_gui = True

# Funktion, um das Bild erneut ohne Dateinameingabe zu speichern
def save_image():
    if img_copy and file_path:
        img_copy.save(file_path)
        update_status(f"Image saved! File name: {file_path}")
    else:
        messagebox.showwarning("Error", "No image loaded to save.")

def save_image_as():
    global img_copy,file_path,timestamp
    if img_copy:  # Check if an image is loaded        
        # Save the image with the provided name
        save_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                     initialfile=f"screenshot_{timestamp}", 
                                                     filetypes=[("PNG files", "*.png"), 
                                                                ("JPEG files", "*.jpg"),
                                                                ("All files", "*.*")])
        if save_path:
            img_copy.save(save_path)
            update_status(f"Image saved! File name: {file_path}")
            file_path = save_path
    else:
        messagebox.showwarning("Warning", "No image loaded to save.")


def is_valid_filename(filename):
    # Define a pattern of invalid characters for most systems
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    reserved_names = [
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    ]
    
    # Check for invalid characters
    if re.search(invalid_chars, filename):
        return False
    
    # Check if the filename is a reserved name in Windows
    if filename.upper() in reserved_names:
        return False
    
    # Check if the filename ends with a space or period (not allowed in Windows)
    if filename.endswith(' ') or filename.endswith('.'):
        return False
    
    # Check if the filename is empty
    if len(filename.strip()) == 0:
        return False
    
    return True

def rename_file():
    global file_path
    old_name = file_path
    # Ask the user for the new name
    new_name = simpledialog.askstring("Input", "New file name?", parent=root)

    # Print the name or handle it further
    if not new_name: 
        messagebox.showwarning("Error", "No name entered.")
        return
    if not is_valid_filename(new_name):
        messagebox.showwarning("Error", "The file name you entered is invalid.")
        return
    
    new_name = os.path.join(desktop_path, f"{new_name}.png")
    os.rename(old_name, new_name)
    file_path = new_name
    update_status(f"Success. New name: {new_name}")      

# Funktion, um das Bild zu öffnen und anzuzeigen
def open_image(file_path):
    global img, photo, img_copy

    img = Image.open(file_path)
    img_copy = img.copy()
    photo = ImageTk.PhotoImage(img_copy)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.config(scrollregion=canvas.bbox(tk.ALL))

def open_image_file():
    global file_path,img_copy
    # Open a file dialog to select the image
    _x = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.bmp;*.gif")])
    
    if _x:
        file_path = _x        
        img = Image.open(file_path)
        img_copy = img.copy()
        open_image(file_path)

# Function to get the color from a color chooser
def choose_color():
    color_code = colorchooser.askcolor(title="Choose line color")
    return color_code[1]  # Returns the hex value of the selected color

# Function to get the line size
def get_line_size():
    global line_width
    if not line_width: line_width = 5
    size = simpledialog.askinteger("Input", "Enter line width:", minvalue=1, maxvalue=20, initialvalue=line_width)
    return size


# Funktion, um Bereiche zu verpixeln
def pixelate_area(x0, y0, x1, y1):
    global img_copy, photo, canvas
    cropped_area = img_copy.crop((x0, y0, x1, y1))
    pixelated_area = cropped_area.resize((10, 10), resample=Image.NEAREST).resize(cropped_area.size, Image.NEAREST)
    img_copy.paste(pixelated_area, (x0, y0, x1, y1))
    photo = ImageTk.PhotoImage(img_copy)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)

# Funktion zum Zuschneiden des Bildes
def crop_image():
    global img_copy, photo, start_x, start_y, end_x, end_y, zuschneiden_mode, canvas

    if start_x is not None and start_y is not None and end_x is not None and end_y is not None:
        img_copy = img_copy.crop((start_x, start_y, end_x, end_y))
        photo = ImageTk.PhotoImage(img_copy)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Funktion, um den Verpixeln-Modus zu aktivieren
def enable_pixelate_mode():
    global pixelate_mode, zuschneiden_mode, paint_mode
    pixelate_mode = True
    zuschneiden_mode = False
    paint_mode = False
    update_status("Pixelation mode is activated. Select an area with the mouse.")

# Funktion, um den Zuschneiden-Modus zu aktivieren
def enable_zuschneiden_mode():
    global pixelate_mode, zuschneiden_mode, paint_mode
    pixelate_mode = False
    zuschneiden_mode = True
    paint_mode = False
    update_status("Cropping mode is activated. Select an area with the mouse.")


# Funktion, um den Paint-Modus zu aktivieren
def enable_paint_mode():
    global paint_mode, pixelate_mode, zuschneiden_mode, chosen_color, line_width
    paint_mode = True
    pixelate_mode = False
    zuschneiden_mode = False

    chosen_color = choose_color()
    line_width = get_line_size()

    update_status("Paint mode is activated. Draw on the canvas with the mouse.")


# Mouse event to start drawing
def on_mouse_down(event):
    global start_x, start_y, current_line, chosen_color, line_width
    start_x = event.x
    start_y = event.y
    if paint_mode:
        # Start a new line
        current_line = canvas.create_line(start_x, start_y, start_x, start_y, fill=chosen_color, width=line_width)

# Mouse event to continue drawing
def on_mouse_drag(event):
    global current_line
    if paint_mode:
        # Update the line as the mouse moves
        canvas.coords(current_line, start_x, start_y, event.x, event.y)

# Mouse event to finish drawing
def on_mouse_up(event):
    global current_line, start_x, start_y, end_x, end_y, img_copy,photo, chosen_color, line_width, canvas
    if paint_mode:
        # Finish the line
        canvas.coords(current_line, start_x, start_y, event.x, event.y)
        current_line = None  # Reset for the next drawing


        # Draw a line on the image
        draw = ImageDraw.Draw(img_copy)
        draw.line([(start_x, start_y), (event.x, event.y)], fill=chosen_color, width=line_width)
        
        img_copy.paste(canvas.coords(current_line, start_x, start_y, event.x, event.y))
        photo = ImageTk.PhotoImage(img_copy)

        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.config(scrollregion=canvas.bbox(tk.ALL))
      

    else:
        # The existing functionality for pixelation and cropping
        
        end_x = event.x
        end_y = event.y

        # If start_x is greater than end_x, swap them
        if start_x > end_x:
            start_x, end_x = end_x, start_x

        # If start_y is greater than end_y, swap them
        if start_y > end_y:
            start_y, end_y = end_y, start_y

        if pixelate_mode:
            pixelate_area(start_x, start_y, end_x, end_y)
        elif zuschneiden_mode:
            crop_image()


# Funktion zum Aktualisieren der Statusleiste
def update_status(new_status):
    status_var.set(new_status)

def exit_program():
    #root.destroy() # Fenster schließen
    root.quit() # Programm beenden

# Show the window
def show():
    root.deiconify()
 
# Hide the window
def hide():
    root.withdraw()

# GUI erstellen
root = tk.Tk()
root.title("Screenshot Tool")

# Menüleiste
menu = tk.Menu(root)
root.config(menu=menu)

# Statusleiste
status_var = tk.StringVar()
status_var.set("Ready")  # Initialer Status

status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor='w')
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Screenshot-Menü
file_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Take a screenshot", command=take_screenshot)
file_menu.add_separator()
file_menu.add_command(label="Open ...", command=open_image_file)
file_menu.add_command(label="Save", command=save_image)
file_menu.add_command(label="Rename ...", command=rename_file)
file_menu.add_command(label="Save as ...", command=save_image_as)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_program)

# Menü zum Zuschneiden und Verpixeln
edit_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Cropping", command=enable_zuschneiden_mode)
edit_menu.add_command(label="Pixelation", command=enable_pixelate_mode)
edit_menu.add_command(label="Draw Line", command=enable_paint_mode)

# Canvas zur Anzeige des Bildes
canvas = tk.Canvas(root)
canvas.pack(fill=tk.BOTH, expand=True)

# Maus-Events für die Auswahl von Bereichen und Zeichnen
canvas.bind("<ButtonPress-1>", on_mouse_down)
canvas.bind("<B1-Motion>", on_mouse_drag)
canvas.bind("<ButtonRelease-1>", on_mouse_up)



# Hauptloop
take_screenshot()
root.mainloop()

