import os, base64, secrets, threading, ctypes, sqlite3, time, hashlib
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.fernet import Fernet
from contextlib import contextmanager

class SecureVault:
    def __init__(self, lock_callback=None):
        self.key = None
        self.db_name = "vault.db"
        self.usb_secret_name = "vault_key.bin"
        self.lock_callback = lock_callback
        self.auto_lock_timer = None
        self._init_db()

    @contextmanager
    def _safe_db(self):
        conn = sqlite3.connect(self.db_name)
        try: yield conn; conn.commit()
        except Exception: conn.rollback(); raise
        finally: conn.close()

    def _init_db(self):
        with self._safe_db() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS entries (service TEXT UNIQUE, user TEXT, pwd TEXT)")
            conn.execute("CREATE TABLE IF NOT EXISTS notes (title TEXT UNIQUE, content TEXT)")
        if not os.path.exists("vault.salt"):
            with open("vault.salt", "wb") as f: f.write(os.urandom(16))

    # --- THE NUCLEAR OPTION ---
    def _handle_failure(self):
        fail_file = "vault.fail"
        count = 0
        if os.path.exists(fail_file):
            with open(fail_file, "r") as f: count = int(f.read())
        count += 1
        if count >= 5:
            self.nuclear_delete()
            return "DESTRUCTED"
        with open(fail_file, "w") as f: f.write(str(count))
        return count

    def nuclear_delete(self):
        for f in [self.db_name, "vault.hash", "vault.salt", "vault.fail"]:
            if os.path.exists(f):
                size = os.path.getsize(f)
                with open(f, "wb") as wb: wb.write(os.urandom(size))
                os.remove(f)

    # --- CRYPTOGRAPHY ---
    def derive_key(self, password, usb_path):
        usb_file = os.path.join(usb_path, self.usb_secret_name)
        if not os.path.exists(usb_file): return False
        with open(usb_file, "rb") as f: hardware_pepper = f.read()
        with open("vault.salt", "rb") as f: salt = f.read()

        kdf = Argon2id(salt=salt, length=32, iterations=3, memory_cost=65536, parallelism=4)
        raw_key = kdf.derive(password.encode() + hardware_pepper)
        self.key = base64.urlsafe_b64encode(raw_key)
        self.reset_lock_timer()
        return True

    def reset_lock_timer(self, timeout=300):
        if self.auto_lock_timer: self.auto_lock_timer.cancel()
        if self.key:
            self.auto_lock_timer = threading.Timer(timeout, self.lock_vault)
            self.auto_lock_timer.daemon = True
            self.auto_lock_timer.start()

    def lock_vault(self):
        self.key = None
        if self.lock_callback: self.lock_callback()
