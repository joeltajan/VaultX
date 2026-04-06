import os
import pickle
import hashlib
from crypto_utils import encrypt_data, decrypt_data

MAGIC_HEADER = b'VAULTx1\x00'

class VaultManager:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.password = None
        self.data = {
            "files": {}
        }

    def is_initialized(self) -> bool:
        return os.path.exists(self.vault_path)

    def load_vault(self, password: str) -> bool:
        if not self.is_initialized():
            return False
            
        with open(self.vault_path, 'rb') as f:
            data = f.read()
            
        if not data.startswith(MAGIC_HEADER):
            raise ValueError("Not a valid vault file.")
            
        payload = data[len(MAGIC_HEADER):]
        if len(payload) < 28:
            raise ValueError("Corrupted vault file.")
            
        salt = payload[:16]
        nonce = payload[16:28]
        ciphertext = payload[28:]
        
        try:
            decrypted = decrypt_data(password, salt, nonce, ciphertext)
            loaded_payload = pickle.loads(decrypted)
            self.password = password
            
            if isinstance(loaded_payload, dict) and "files" not in loaded_payload:
                self.data = {
                    "files": loaded_payload
                }
            else:
                self.data = loaded_payload
                
            return True
        except Exception:
            raise ValueError("Incorrect Password or Corrupted Vault.")

    def save_vault(self) -> bool:
        if not self.password:
            raise ValueError("No password set.")
            
        pickled_data = pickle.dumps(self.data)
        salt, nonce, ciphertext = encrypt_data(self.password, pickled_data)
        
        with open(self.vault_path, 'wb') as f:
            f.write(MAGIC_HEADER)
            f.write(salt)
            f.write(nonce)
            f.write(ciphertext)
        return True

    def initialize_new(self, password: str):
        self.password = password
        self.data = {
            "files": {}
        }
        self.save_vault()

    def wipe_vault(self):
        self.data = {"files": {}}
        self.password = None
        if os.path.exists(self.vault_path):
            try:
                os.remove(self.vault_path)
            except OSError:
                pass

    # --- MEMORY FILESYSTEM ---
    def add_file(self, file_path: str):
        filename = os.path.basename(file_path)
        mtime = os.path.getmtime(file_path)
        with open(file_path, 'rb') as f:
            content = f.read()
            
        self.data["files"][filename] = {
            "content": content,
            "size": len(content),
            "modified": mtime
        }
        self.save_vault()

    def get_file_content(self, filename: str) -> bytes:
        entry = self.data["files"].get(filename)
        if not entry:
            return None
        if isinstance(entry, bytes):
            return entry
        return entry.get("content")

    def export_file(self, filename: str, dest_path: str):
        content = self.get_file_content(filename)
        if content is not None:
            with open(dest_path, 'wb') as f:
                f.write(content)

    def remove_file(self, filename: str):
        if filename in self.data["files"]:
            del self.data["files"][filename]
            self.save_vault()
            
    def list_files(self) -> list:
        result = []
        for k, v in self.data["files"].items():
            if isinstance(v, bytes):
                result.append((k, len(v), 0.0))
            else:
                result.append((k, v.get("size", 0), v.get("modified", 0.0)))
        return result
