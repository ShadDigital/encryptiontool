import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import ctypes
from tkinter import messagebox
import requests
import subprocess
import sys
import hashlib

class EncryptionTool(TkinterDnD.Tk):
    VERSION = "1.0.0"

    def __init__(self):
        super().__init__()

        self.title("Encryption Tool")
        self.geometry("600x450")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.label = ctk.CTkLabel(self, text="Encrypter", font=("Fixedsys", 36, "bold"))
        self.label.pack(pady=20)

        self.drop_frame = ctk.CTkFrame(self, width=500, height=200, border_width=2, border_color="#333")
        self.drop_frame.pack(pady=20, padx=20)
        self.drop_frame.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(self.drop_frame, text="Drag & Drop File Here\nto Encrypt/Decrypt", text_color="gray")
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.file_dropped)

        # Add this near the bottom of your __init__
        self.action_button = ctk.CTkButton(self, text="Encrypt/Decrypt", command=self.process_vault, state="disabled")
        self.action_button.pack(pady=20)
        # We don't call .pack() here so it stays hidden

        try:
            basedir = os.path.dirname(os.path.abspath(__file__))
            dll_path = os.path.join(basedir, "encryptor.dll")
            
            # Load the DLL using the full absolute path
            self.encryptor = ctypes.CDLL(dll_path)
            
            self.encryptor.process_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
            self.encryptor.process_file.restype = ctypes.c_bool
        except Exception as e:
            print(f"DLL Load Error: {e}")
            # This prevents the app from crashing later by giving it a dummy value
            self.encryptor = None
    
    def file_dropped(self, event):
        # when mouse button is released
        file_path = event.data.strip("{}")
        self.drop_label.configure(text=f"Selected:\n{os.path.basename(file_path)}", text_color="#1f538d")
        self.selected_file = file_path

        # This just places the existing button on the screen 
        # (It won't create a second one if it's already there)
        self.action_button.configure(state="normal")
        
    
    def process_vault(self):
        if not hasattr(self, 'encryptor') or self.encryptor is None:
            messagebox.showerror("Engine Error", "C++ Encryption Engine not found!")
            return
        if hasattr(self, 'selected_file'):
            input_path = self.selected_file
            output_path = input_path + ".vault"
            key = "ROBOTICS_SHIELD_2026"

            b_input = input_path.encode('utf-8')
            b_output = output_path.encode('utf-8')
            b_key = key.encode('utf-8')

            success = self.encryptor.process_file(b_input, b_output, b_key)

            if success:
                messagebox.showinfo("Vault", "Shield Initialized: File Encrypted!")
            else:
                messagebox.showerror("Vault", "Encryption failed in C++ engine.")
        else:
            messagebox.showwarning("Warning", "No file selected!")
    def run_silent_update(self, download_url, expected_hash_url):
        try:
            response = requests.get(download_url)
            with open("main_new.py", "wb") as f:
                f.write(response.content)
            
            expected_hash = requests.get(expected_hash_url).text.strip().lower()

            normalized_content = response.content.replace(b"\r\n", b"\n")
        
            actual_hash = hashlib.sha256(normalized_content).hexdigest().lower()

            print(f"DEBUG: I got from GitHub: [{expected_hash}]")
            print(f"DEBUG: I calculated:    [{actual_hash}]")

            if actual_hash != expected_hash:
                messagebox.showerror("Security Error", "Update verification failed! Fingerprint mismatch.")
                os.remove("main_new.py") # Delete the "bad" file
                return
            
            with open("patcher.bat", "w") as f:
                f.write(f"""
                @echo off
                timeout /t 2 /nobreak > nul
                move /y main_new.py main.py
                start python main.py
                del patcher.bat
                """)

            subprocess.Popen(["patcher.bat"], shell=True)
            sys.exit()
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to install update: {e}")


if __name__ == "__main__":
    app = EncryptionTool()

    repo_base = "https://raw.githubusercontent.com/ShadDigital/encryptiontool/main/"
    python_url = repo_base + "main.py"
    hash_url = repo_base + "main_hash.txt"
    app.after(1000, lambda: app.run_silent_update(python_url, hash_url))
    app.mainloop()
