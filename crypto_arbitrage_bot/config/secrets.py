"""
Encrypted secrets storage for sensitive credentials (e.g., API tokens).
Uses Fernet symmetric encryption from the cryptography package.
"""
import os
from cryptography.fernet import Fernet

SECRETS_FILE = "secrets.enc"
KEY_FILE = "secrets.key"

class SecretsManager:
    def __init__(self, key_path=KEY_FILE, secrets_path=SECRETS_FILE):
        self.key_path = key_path
        self.secrets_path = secrets_path
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)

    def _load_or_create_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                return f.read()
        key = Fernet.generate_key()
        with open(self.key_path, "wb") as f:
            f.write(key)
        return key

    def save_secret(self, name, value):
        secrets = self.load_secrets()
        secrets[name] = value
        data = str(secrets).encode()
        encrypted = self.fernet.encrypt(data)
        with open(self.secrets_path, "wb") as f:
            f.write(encrypted)

    def load_secrets(self):
        if not os.path.exists(self.secrets_path):
            return {}
        with open(self.secrets_path, "rb") as f:
            encrypted = f.read()
        try:
            data = self.fernet.decrypt(encrypted)
            return eval(data.decode())
        except Exception:
            return {}

    def get_secret(self, name):
        secrets = self.load_secrets()
        return secrets.get(name)

# Usage example:
# secrets = SecretsManager()
# secrets.save_secret("telegram_api_token", "YOUR_TOKEN_HERE")
# token = secrets.get_secret("telegram_api_token")
