import os
import shutil
import hashlib
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

destination_root = "C:/photos"
is_running = False
copied_files = set()
copied_count = 0

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_copied_files():
    global copied_files
    copied_files.clear()
    for folder_number in range(1, 10000):
        folder_path = os.path.join(destination_root, str(folder_number))
        if not os.path.exists(folder_path):
            break
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                copied_files.add(get_file_hash(file_path))

def reset_copied_files():
    copied_files.clear()

def get_next_folder():
    folder_number = 1
    while True:
        folder_path = os.path.join(destination_root, str(folder_number))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return folder_path
        if len(os.listdir(folder_path)) < 500:
            return folder_path
        folder_number += 1

def copy_images(source_folder, status_label, log_output):
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
                    log_output.insert(tk.END, f"Pominięto: {file}\n")
                    log_output.yview(tk.END)
                    continue  
                
                destination_folder = get_next_folder()
                destination_path = os.path.join(destination_folder, file)
                
                shutil.copy2(file_path, destination_path)
                copied_files.add(file_hash)
                copied_count += 1
                status_label.config(text=f"Skopiowano: {copied_count} zdjęć")
                log_output.insert(tk.END, f"Skopiowano: {file} -> {destination_path}\n")
                log_output.yview(tk.END)
    
    is_running = False
    status_label.config(text="Zakończono kopiowanie")
    log_output.insert(tk.END, "Zakończono kopiowanie.\n")
    log_output.yview(tk.END)

def start_copying(status_label, log_output):
    global is_running
    if is_running:
        return
    
    source_folder = filedialog.askdirectory()
    if not source_folder:
        return
    
    is_running = True
    status_label.config(text="Rozpoczęto kopiowanie...")
    log_output.insert(tk.END, "Rozpoczęto kopiowanie...\n")
    log_output.yview(tk.END)
    threading.Thread(target=copy_images, args=(source_folder, status_label, log_output), daemon=True).start()

def stop_copying(status_label, log_output):
    global is_running
    is_running = False
    status_label.config(text="Zatrzymano kopiowanie")
    log_output.insert(tk.END, "Zatrzymano kopiowanie.\n")
    log_output.yview(tk.END)

def create_gui():
    root = tk.Tk()
    root.title("Photo Copier")
    root.geometry("400x300")
    
    status_label = tk.Label(root, text="", fg="blue")
    status_label.pack(pady=5)
    
    start_button = tk.Button(root, text="Start", command=lambda: start_copying(status_label, log_output), width=20)
    start_button.pack(pady=5)
    
    stop_button = tk.Button(root, text="Stop", command=lambda: stop_copying(status_label, log_output), width=20)
    stop_button.pack(pady=5)
    
    reset_button = tk.Button(root, text="Reset Kopiowania", command=reset_copied_files, width=20)
    reset_button.pack(pady=5)
    
    log_output = scrolledtext.ScrolledText(root, width=50, height=10, bg="white", fg="black")
    log_output.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
