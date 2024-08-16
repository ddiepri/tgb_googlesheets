import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
AUTHORIZED_CHAT_ID = int(os.getenv('AUTHORIZED_CHAT_ID'))