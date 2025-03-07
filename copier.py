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
    existing_folders = sorted(
        [f for f in os.listdir(destination_root) if f.isdigit()],
        key=lambda x: int(x)
    )
    
    for folder_name in existing_folders:
        folder_path = os.path.join(destination_root, folder_name)
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                copied_files.add(get_file_hash(file_path))

def get_next_folder():
    existing_folders = sorted(
        [f for f in os.listdir(destination_root) if f.isdigit()],
        key=lambda x: int(x)
    )
    
    for folder_name in existing_folders:
        folder_path = os.path.join(destination_root, folder_name)
        if len(os.listdir(folder_path)) < 500:
            return folder_path

    new_folder_number = 1 if not existing_folders else int(existing_folders[-1]) + 1
    new_folder_path = os.path.join(destination_root, str(new_folder_number))
    os.makedirs(new_folder_path)
    return new_folder_path

def copy_images(source_folder, status_label, log_output, start_button):
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
                    log_output.insert(tk.END, f"Plik: {file} już jest skopiowany.\n")
                    log_output.yview(tk.END)
                    continue  
                
                destination_folder = get_next_folder()
                destination_path = os.path.join(destination_folder, file)
                
                shutil.copy2(file_path, destination_path)
                copied_files.add(file_hash)
                copied_count += 1
                status_label.config(text=f"Skopiowano: {copied_count} zdjęć")
                log_output.insert(tk.END, f"Skopiowano: {destination_path}\n")
                log_output.yview(tk.END)
    
    is_running = False
    status_label.config(text=f"Zakończono kopiowanie. Skopiowano: {copied_count} zdjęć")
    log_output.insert(tk.END, "Zakończono kopiowanie.\n")
    log_output.yview(tk.END)
    start_button.config(state=tk.NORMAL)

def start_copying(status_label, log_output, start_button):
    global is_running
    if is_running:
        return
    
    source_folder = filedialog.askdirectory()
    if not source_folder:
        return
    
    is_running = True
    status_label.config(text="Rozpoczęto kopiowanie...")
    log_output.insert(tk.END, "Rozpoczęto kopiowanie i przeliczanie duplikatów...\n")
    log_output.yview(tk.END)
    start_button.config(state=tk.DISABLED)
    threading.Thread(target=copy_images, args=(source_folder, status_label, log_output, start_button), daemon=True).start()

def stop_copying(status_label, log_output, start_button):
    global is_running
    is_running = False
    status_label.config(text="Zatrzymano kopiowanie")
    log_output.insert(tk.END, "Zatrzymano kopiowanie.\n")
    log_output.yview(tk.END)
    start_button.config(state=tk.NORMAL)

def select_output_folder(output_label):
    global destination_root
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        destination_root = folder_selected
        output_label.config(text=f"Folder docelowy: {destination_root}")

def create_gui():
    root = tk.Tk()
    root.title("Photo Copier")
    root.geometry("600x400")
    
    status_label = tk.Label(root, text="", fg="blue")
    status_label.pack(pady=5)
    
    start_button = tk.Button(root, text="Start", command=lambda: start_copying(status_label, log_output, start_button), width=20)
    start_button.pack(pady=5)
    
    stop_button = tk.Button(root, text="Stop", command=lambda: stop_copying(status_label, log_output, start_button), width=20)
    stop_button.pack(pady=5)
    
    output_label = tk.Label(root, text=f"Kopiowanie do folderu: {destination_root}", fg="black")
    output_label.pack(pady=5)
    
    select_output_button = tk.Button(root, text="Zmień folder docelowy", command=lambda: select_output_folder(output_label), width=20)
    select_output_button.pack(pady=5)
    
    log_output = scrolledtext.ScrolledText(root, width=70, height=12, bg="white", fg="black")
    log_output.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
