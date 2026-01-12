def _handle_failure(self):
        """Increments failure count and triggers deletion if limit reached."""
        fail_file = "vault.fail"
        count = 0
        
        if os.path.exists(fail_file):
            with open(fail_file, "r") as f:
                count = int(f.read())
        
        count += 1
        
        if count >= 5:
            self.nuclear_delete()
            return "DESTRUCTED"
        
        with open(fail_file, "w") as f:
            f.write(str(count))
        return count

    def reset_failures(self):
        """Clears the failure counter on successful login."""
        if os.path.exists("vault.fail"):
            os.remove("vault.fail")

    def nuclear_delete(self):
        """Wipes the database and sensitive files."""
        files_to_wipe = [self.db_name, "vault.hash", "vault.salt", "vault.fail"]
        for file in files_to_wipe:
            if os.path.exists(file):
                # For extra safety, we overwrite with random data before deleting
                file_size = os.path.getsize(file)
                with open(file, "wb") as f:
                    f.write(os.urandom(file_size))
                os.remove(file)
        print("CRITICAL: Vault destroyed due to multiple failed login attempts.")






def attempt_login(self):
        password = self.master_entry.get()
        usb_path = self.usb_entry.get()
        
        if self.vault.derive_key(password, usb_path):
            if self.vault.verify_login(password):
                self.vault.reset_failures() # Success!
                self.show_dashboard()
            else:
                self.process_failure()
        else:
            self.process_failure()

    def process_failure(self):
        result = self.vault._handle_failure()
        if result == "DESTRUCTED":
            messagebox.showerror("TERMINATED", "5 failed attempts. Vault has been wiped for your security.")
            self.quit()
        else:
            messagebox.showwarning("Access Denied", f"Invalid login. {5 - result} attempts remaining.")
