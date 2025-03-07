import os
import shutil
import hashlib
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

destination_root = "C:/photos"
is_running = False
copied_files = set()
copied_count = 0

def get_file_hash(file_path):
    """Oblicza skrót pliku, aby uniknąć duplikatów."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_copied_files():
    """Wczytuje listę już skopiowanych plików."""
    global copied_files
    if os.path.exists("copied_files.txt"):
        with open("copied_files.txt", "r") as f:
            copied_files = set(f.read().splitlines())

def save_copied_file(file_hash):
    """Zapisuje informację o skopiowanym pliku."""
    with open("copied_files.txt", "a") as f:
        f.write(file_hash + "\n")

def get_next_folder():
    """Znajduje lub tworzy kolejny folder do przechowywania zdjęć."""
    folder_number = 1
    while True:
        folder_path = os.path.join(destination_root, str(folder_number))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return folder_path
        if len(os.listdir(folder_path)) < 500:
            return folder_path
        folder_number += 1

def copy_images(source_folder, status_label):
    """Funkcja kopiująca obrazy do katalogów w tle."""
    global is_running, copied_count
    load_copied_files()
    copied_count = 0
    
    for root, _, files in os.walk(source_folder):
        if not is_running:
            break
        
        for file in files:
            if not is_running:
                break
            
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                file_path = os.path.join(root, file)
                file_hash = get_file_hash(file_path)
                
                if file_hash in copied_files:
                    continue  # Plik już został skopiowany
                
                destination_folder = get_next_folder()
                destination_path = os.path.join(destination_folder, file)
                
                shutil.copy2(file_path, destination_path)
                copied_files.add(file_hash)
                save_copied_file(file_hash)
                copied_count += 1
                status_label.config(text=f"Skopiowano: {copied_count} zdjęć")
    
    is_running = False
    status_label.config(text="Zakończono kopiowanie")

def start_copying(status_label):
    """Rozpoczyna kopiowanie w osobnym wątku."""
    global is_running
    if is_running:
        return
    
    source_folder = filedialog.askdirectory()
    if not source_folder:
        return
    
    is_running = True
    status_label.config(text="Rozpoczęto kopiowanie...")
    threading.Thread(target=copy_images, args=(source_folder, status_label), daemon=True).start()

def stop_copying(status_label):
    """Zatrzymuje proces kopiowania."""
    global is_running
    is_running = False
    status_label.config(text="Zatrzymano kopiowanie")

def create_gui():
    """Tworzy GUI aplikacji."""
    root = tk.Tk()
    root.title("Photo Organizer")
    root.geometry("300x200")
    
    status_label = tk.Label(root, text="", fg="blue")
    status_label.pack(pady=10)
    
    start_button = tk.Button(root, text="Start", command=lambda: start_copying(status_label), width=20)
    start_button.pack(pady=10)
    
    stop_button = tk.Button(root, text="Stop", command=lambda: stop_copying(status_label), width=20)
    stop_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
