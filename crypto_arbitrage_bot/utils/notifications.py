# Notification system

import requests
from config.secrets import SecretsManager

class TelegramNotifier:
    def __init__(self):
        self.secrets = SecretsManager()
        self.token = self.secrets.get_secret("telegram_api_token")
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None

    def send_message(self, chat_id, text):
        if not self.base_url:
            raise ValueError("Telegram API token not set.")
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)
        return response.json()

# Usage example:
# notifier = TelegramNotifier()
# notifier.send_message(chat_id="YOUR_CHAT_ID", text="Test message from bot!")
