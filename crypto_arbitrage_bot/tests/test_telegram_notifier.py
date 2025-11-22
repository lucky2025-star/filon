import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.notifications import TelegramNotifier
from config.secrets import SecretsManager

# Save your Telegram API token securely (run once)
secrets = SecretsManager()
secrets.save_secret("telegram_api_token", "8207262508:AAHJqs7gkmmYhHe4TAecsyEwbKiScK3B1yA")

# Test sending a message
notifier = TelegramNotifier()
chat_id = "1395251148"  # Your provided chat ID
response = notifier.send_message(chat_id, "Test message from crypto arbitrage bot!")
print(response)
