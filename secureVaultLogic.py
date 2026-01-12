def generate_recovery_kit(self, usb_path):
        """Generates a text-based recovery kit for physical printing."""
        usb_file = os.path.join(usb_path, self.usb_secret_name)
        if not os.path.exists(usb_file):
            return "Error: USB not found."

        with open(usb_file, "rb") as f:
            hardware_secret = base64.b64encode(f.read()).decode()

        kit_content = f"""
        ==================================================
        CIPHERVAULT ULTRA - EMERGENCY RECOVERY KIT
        ==================================================
        DATE GENERATED: {time.strftime("%Y-%m-%d %H:%M:%S")}
        
        HARDWARE KEY (USB PEPPER):
        {hardware_secret}
        
        INSTRUCTIONS:
        1. If your USB drive is lost, copy the 'HARDWARE KEY' above.
        2. Create a new file named 'vault_key.bin' on a new USB.
        3. Paste the decoded bytes of the key into that file.
        
        WARNING: Keep this paper in a fireproof safe. 
        Anyone with this paper can access your vault.
        ==================================================
        """
        
        with open("RECOVERY_KIT_PRINT_AND_DELETE.txt", "w") as f:
            f.write(kit_content)
        
        return "RECOVERY_KIT_PRINT_AND_DELETE.txt"
