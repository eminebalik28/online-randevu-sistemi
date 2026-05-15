"""
main.py
───────
Uygulamanın giriş noktası.

Görev: Modülleri bir araya getirir, DatabaseManager'ı
başlatır ve Tkinter arayüzünü (Uygulama) başlatarak ana döngüyü açar.

Kullanım:
    python main.py

Varsayılan Admin:
    Kullanıcı adı : admin
    Şifre         : admin123
"""

import sys
import os

# Çalışma dizinini projenin kök dizinine sabitle
# (farklı konumdan çalıştırma senaryosunu destekler)
PROJE_DIZINI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJE_DIZINI)

from database import DatabaseManager
from gui import Uygulama


def main():
    """
    Uygulamanın ana başlatma fonksiyonu.

    Adımlar:
      1. Veritabanı bağlantısını kur (tablo yoksa oluştur).
      2. Tkinter arayüzünü (Uygulama) başlat.
      3. Arayüz kapatılana kadar mainloop'u çalıştır.
    """
    print("\n  Sistem başlatılıyor...")
    db = DatabaseManager(db_yolu=os.path.join(PROJE_DIZINI, "randevu_sistemi.db"))
    print("  Veritabanı bağlantısı kuruldu. ✓\n")

    app = Uygulama(db)
    app.mainloop()


if __name__ == "__main__":
    main()
