import sqlite3
import os

db_yolu = os.path.join(os.path.dirname(os.path.abspath(__file__)), "randevu_sistemi.db")

doktorlar = [
    ("Oğuzhan Koç", "Diş Hekimliği", "09:00,10:00,13:00,14:00"),
    ("Merve Nur", "Çocuk Sağlığı", "09:00,11:00,14:00,16:00"),
    ("Kemal Sunal", "Genel Cerrahi", "10:00,14:00"),
    ("Eda Ece", "Fizik Tedavi", "09:00,11:00,13:00,15:00"),
    ("Büşra Pekin", "Beslenme ve Diyet", "10:00,11:00,14:00,15:00"),
    ("Haluk Bilginer", "Göğüs Hastalıkları", "09:00,11:00,14:00"),
    ("Gülse Birsel", "Onkoloji", "10:00,13:00,15:00"),
    ("Beren Saat", "Kadın Doğum", "09:00,10:00,11:00,14:00"),
    ("Kıvanç Tatlıtuğ", "Plastik Cerrahi", "10:00,14:00,16:00"),
    ("Serenay Sarıkaya", "Ortodonti", "09:00,11:00,15:00"),
    ("Tolga Çevik", "Romatoloji", "10:00,11:00,13:00"),
    ("Demet Evgar", "Hematoloji", "09:00,10:00,14:00"),
    ("Çağatay Ulusoy", "Endokrinoloji", "11:00,14:00,15:00"),
    ("Fahriye Evcen", "Gastroenteroloji", "09:00,11:00,14:00")
]

conn = sqlite3.connect(db_yolu)
for ad, uzmanlik, saatler in doktorlar:
    # Check if already exists to prevent duplicates
    mevcut = conn.execute("SELECT 1 FROM Doktorlar WHERE ad = ? AND uzmanlik = ?", (ad, uzmanlik)).fetchone()
    if not mevcut:
        conn.execute("INSERT INTO Doktorlar (ad, uzmanlik, uygun_saatler) VALUES (?, ?, ?)", (ad, uzmanlik, saatler))

conn.commit()
conn.close()
print("Eksik doktorlar eklendi.")
