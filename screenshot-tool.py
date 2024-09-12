import pyautogui
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime
from time import sleep

# Variablen zum Speichern des Dateipfads und der Image-Objekte
file_path = None
desktop_path = None
img = None
img_copy = None
pixelate_mode = False  # Verpixeln-Modus deaktiviert
zuschneiden_mode = False  # Zuschneiden-Modus deaktiviert

# Funktion, um einen Screenshot zu machen
def take_screenshot():
    global img, img_copy, file_path,desktop_path

    hide()
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

    # enable_crop_button()  # Zuschneiden aktivieren

    show()

    root.state('zoomed')  # Vollbildmodus

# Funktion, um das Bild erneut ohne Dateinameingabe zu speichern
def save_image():
    if img_copy and file_path:
        img_copy.save(file_path)
        update_status(f"Gespeichert. Das Bild wurde erfolgreich unter {file_path} gespeichert.")
    else:
        messagebox.showwarning("Fehler", "Kein Bild zum Speichern gefunden.")

# Funktion, um das Bild zu öffnen und anzuzeigen
def open_image(file_path):
    global img, photo, img_copy

    img = Image.open(file_path)
    img_copy = img.copy()
    photo = ImageTk.PhotoImage(img_copy)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Funktion, um Bereiche zu verpixeln
def pixelate_area(x0, y0, x1, y1):
    global img_copy, photo
    cropped_area = img_copy.crop((x0, y0, x1, y1))
    pixelated_area = cropped_area.resize((10, 10), resample=Image.NEAREST).resize(cropped_area.size, Image.NEAREST)
    img_copy.paste(pixelated_area, (x0, y0, x1, y1))
    photo = ImageTk.PhotoImage(img_copy)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)

# Funktion zum Zuschneiden des Bildes
def crop_image():
    global img_copy, photo, start_x, start_y, end_x, end_y, zuschneiden_mode

    if start_x is not None and start_y is not None and end_x is not None and end_y is not None:
        img_copy = img_copy.crop((start_x, start_y, end_x, end_y))
        photo = ImageTk.PhotoImage(img_copy)
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Funktion, um den Verpixeln-Modus zu aktivieren
def enable_pixelate_mode():
    global pixelate_mode
    global zuschneiden_mode
    pixelate_mode = True
    zuschneiden_mode = False
    # messagebox.showinfo("Modus aktiviert", "Verpixeln-Modus ist aktiviert. Wähle einen Bereich mit der Maus aus.")
    update_status("Verpixeln-Modus ist aktiviert. Wähle einen Bereich mit der Maus aus.")

# Funktion, um den Zuschneiden-Modus zu aktivieren
def enable_zuschneiden_mode():
    global pixelate_mode
    global zuschneiden_mode
    pixelate_mode = False
    zuschneiden_mode = True
    # messagebox.showinfo("Modus aktiviert", "Zuschneiden-Modus ist aktiviert. Wähle einen Bereich mit der Maus aus.")
    update_status("Zuschneiden-Modus ist aktiviert. Wähle einen Bereich mit der Maus aus.")


# Funktion, um den ausgewählten Bereich zu markieren
def on_mouse_down(event):
    global start_x, start_y
    start_x = event.x
    start_y = event.y

def on_mouse_up(event):
    global start_x, start_y, end_x, end_y
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

def rename():
    global file_path
    old_name = file_path
    # Ask the user for the new name
    new_name = simpledialog.askstring("Input", "Neuer Name?", parent=root)

    # Print the name or handle it further
    if new_name:
        new_name = os.path.join(desktop_path, f"screenshot_{new_name}.png")
        os.rename(old_name, new_name)
        file_path = new_name
        update_status(f"Datei umbenannt.")
    else:
        messagebox.showwarning("Fehler", "No name entered.")

# Funktion zum Aktualisieren der Statusleiste
def update_status(new_status):
    status_var.set(new_status)

def exit_program():
    root.destroy() # Fenster schließen
    # root.quit() # Programm beenden

# Show the window
def show():
    root.deiconify()
 
# Hide the window
def hide():
    root.withdraw()


# GUI erstellen
root = tk.Tk()
root.title("Screenshot-Tool")

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
menu.add_cascade(label="Datei", menu=file_menu)
file_menu.add_command(label="Screenshot aufnehmen", command=take_screenshot)
file_menu.add_command(label="Bild speichern", command=save_image)
file_menu.add_command(label="Bild umbenennen", command=rename)
file_menu.add_command(label="Beenden", command=exit_program)

# Menü zum Zuschneiden und Verpixeln
edit_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Bearbeiten", menu=edit_menu)
edit_menu.add_command(label="Bild zuschneiden", command=enable_zuschneiden_mode)
edit_menu.add_command(label="Verpixeln", command=enable_pixelate_mode)

# Canvas zur Anzeige des Bildes
canvas = tk.Canvas(root)
canvas.pack(fill=tk.BOTH, expand=True)

# Variablen für Mausposition
start_x, start_y, end_x, end_y = None, None, None, None

# Maus-Events für die Auswahl von Bereichen
canvas.bind("<ButtonPress-1>", on_mouse_down)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

# Hauptloop
take_screenshot()
root.mainloop()

