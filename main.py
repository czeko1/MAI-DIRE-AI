import customtkinter as ctk
from tkinter import messagebox
from vault import SecureVault
import pyperclip, secrets

class CipherVaultUltra(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.vault = SecureVault(lock_callback=self.handle_auto_lock)
        self.title("CipherVault Ultra v1.0")
        self.geometry("700x800")
        ctk.set_appearance_mode("dark")
        self.show_login()

    def handle_auto_lock(self):
        self.after(0, self.show_login)
        self.after(0, lambda: messagebox.showwarning("Security", "Vault Locked (Inactivity/USB removed)"))

    def show_login(self):
        for w in self.winfo_children(): w.destroy()
        ctk.CTkLabel(self, text="CIPHERVAULT ULTRA", font=("Fixedsys", 32)).pack(pady=30)
        
        self.usb_entry = ctk.CTkEntry(self, placeholder_text="USB Drive (e.g., D:/)", width=350)
        self.usb_entry.pack(pady=5)
        self.master_entry = ctk.CTkEntry(self, show="*", width=350, placeholder_text="Master Password")
        self.master_entry.pack(pady=5)

        # Virtual Keyboard
        vk_frame = ctk.CTkFrame(self)
        vk_frame.pack(pady=20)
        keys = list("1234567890abcdefghijklmnopqrstuvwxyz!@#$%^&*")
        secrets.SystemRandom().shuffle(keys)
        for i, k in enumerate(keys):
            ctk.CTkButton(vk_frame, text=k, width=40, height=40, 
                          command=lambda val=k: self.master_entry.insert("end", val)).grid(row=i//10, column=i%10, padx=2, pady=2)

        ctk.CTkButton(self, text="UNLOCK VAULT", fg_color="#2ecc71", command=self.attempt_login).pack(pady=20)

    def attempt_login(self):
        if self.vault.derive_key(self.master_entry.get(), self.usb_entry.get()):
            self.show_dashboard()
        else:
            res = self.vault._handle_failure()
            if res == "DESTRUCTED": 
                messagebox.showerror("TERMINATED", "Vault Wiped.")
                self.quit()
            else:
                messagebox.showerror("Denied", f"Access Denied. {5-res} attempts left.")

    def show_dashboard(self):
        for w in self.winfo_children(): w.destroy()
        # Dashboard would include Search, Add Password, and the Secure Notes tab.
        ctk.CTkLabel(self, text="VAULT UNLOCKED", text_color="#2ecc71").pack(pady=10)
        ctk.CTkButton(self, text="Generate Recovery Kit", command=self.make_kit).pack(pady=5)

    def make_kit(self):
        path = self.vault.generate_recovery_kit(self.usb_entry.get())
        messagebox.showinfo("Recovery", f"Kit saved to {path}. PRINT AND DELETE IT NOW.")

if __name__ == "__main__":
    app = CipherVaultUltra()
    app.mainloop()
