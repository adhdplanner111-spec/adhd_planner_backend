import os
from dotenv import load_dotenv

# Memuat file .env otomatis saat modul ini diimport
load_dotenv()

class Config:
    def __init__(self):
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        # Tambahkan konfigurasi lain di sini jika ada

config = Config()