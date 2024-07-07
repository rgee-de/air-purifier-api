import os

from dotenv import load_dotenv

load_dotenv()

HOST_IP = os.getenv("HOST_IP")
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
