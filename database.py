"""
database.py
───────────
Veritabanı bağlantısı, tablo oluşturma ve tüm CRUD
operasyonlarını yöneten DatabaseManager sınıfı.
"""

import sqlite3
import hashlib
from typing import Optional


# ────────────────────────────────────────────
#  YARDIMCI FONKSİYON
# ────────────────────────────────────────────

def sifre_hashle(sifre: str) -> str:
    """Şifreyi SHA-256 ile güvenli biçimde hashler."""
    return hashlib.sha256(sifre.encode("utf-8")).hexdigest()


# ────────────────────────────────────────────
#  VERİTABANI YÖNETİCİSİ
# ────────────────────────────────────────────

class DatabaseManager:
    """
    SQLite veritabanı üzerinde tüm CRUD işlemlerini
    kapsayan merkezi yönetim sınıfı.

    Attributes:
        db_yolu (str): Veritabanı dosyasının yolu.
    """

    def __init__(self, db_yolu: str = "randevu_sistemi.db"):
        self.db_yolu = db_yolu
        self._tabloları_olustur()
        self._doktor_tablosunu_guncelle()
        self._varsayilan_admin_ekle()
        self._ornek_doktorlari_ekle()
        self._mevcut_doktorlara_hesap_olustur()

    def _doktor_tablosunu_guncelle(self):
        """Mevcut veritabanında Doktorlar tablosuna kullanici_adi ve sifre_hash ekler."""
        with self._baglanti() as conn:
            try:
                conn.execute("ALTER TABLE Doktorlar ADD COLUMN kullanici_adi TEXT")
            except sqlite3.OperationalError:
                pass
            try:
                conn.execute("ALTER TABLE Doktorlar ADD COLUMN sifre_hash TEXT")
            except sqlite3.OperationalError:
                pass

    def _mevcut_doktorlara_hesap_olustur(self):
        """Kullanıcı adı atanmamış eski doktorlara varsayılan hesap açar."""
        with self._baglanti() as conn:
            rows = conn.execute("SELECT doktor_id, ad FROM Doktorlar WHERE kullanici_adi IS NULL").fetchall()
            for r in rows:
                ka = r["ad"].lower().replace(" ", "").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ı", "i").replace("ö", "o").replace("ç", "c")
                sifre = sifre_hashle("1234")
                try:
                    conn.execute("UPDATE Doktorlar SET kullanici_adi=?, sifre_hash=? WHERE doktor_id=?", (ka, sifre, r["doktor_id"]))
                except sqlite3.IntegrityError:
                    conn.execute("UPDATE Doktorlar SET kullanici_adi=?, sifre_hash=? WHERE doktor_id=?", (f"{ka}{r['doktor_id']}", sifre, r["doktor_id"]))
            conn.commit()

    # ── BAĞLANTI ─────────────────────────────

    def _baglanti(self) -> sqlite3.Connection:
        """Her işlem için taze bir bağlantı döndürür."""
        conn = sqlite3.connect(self.db_yolu)
        conn.row_factory = sqlite3.Row   # Sütun adıyla erişim
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ── TABLO OLUŞTURMA ───────────────────────

    def _tabloları_olustur(self):
        """Dört ana tabloyu oluşturur; varsa atlar."""
        sql_ifadeleri = [
            """
            CREATE TABLE IF NOT EXISTS Adminler (
                admin_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_adi TEXT    UNIQUE NOT NULL,
                sifre_hash    TEXT    NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Doktorlar (
                doktor_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                ad            TEXT NOT NULL,
                uzmanlik      TEXT NOT NULL,
                uygun_saatler TEXT NOT NULL,
                kullanici_adi TEXT UNIQUE,
                sifre_hash    TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Hastalar (
                hasta_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                ad         TEXT UNIQUE NOT NULL,
                tc         TEXT UNIQUE NOT NULL,
                telefon    TEXT,
                sifre_hash TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS Randevular (
                randevu_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih      TEXT    NOT NULL,
                saat       TEXT    NOT NULL,
                doktor_id  INTEGER NOT NULL,
                hasta_id   INTEGER NOT NULL,
                durum      TEXT    DEFAULT 'Aktif',
                FOREIGN KEY (doktor_id) REFERENCES Doktorlar(doktor_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (hasta_id)  REFERENCES Hastalar(hasta_id)
                    ON DELETE CASCADE
            )
            """,
        ]
        with self._baglanti() as conn:
            for sql in sql_ifadeleri:
                conn.execute(sql)
            conn.commit()

    def _varsayilan_admin_ekle(self):
        """İlk çalıştırmada varsayılan admin hesabını oluşturur."""
        with self._baglanti() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO Adminler (kullanici_adi, sifre_hash) VALUES (?, ?)",
                ("admin", sifre_hashle("admin123")),
            )
            conn.commit()

    def _ornek_doktorlari_ekle(self):
        """Veritabanında hiç doktor yoksa, varsayılan uzmanlık alanlarını ve doktorları ekler."""
        with self._baglanti() as conn:
            # Sistemde doktor var mı kontrol et
            sayi = conn.execute("SELECT COUNT(*) FROM Doktorlar").fetchone()[0]
            if sayi == 0:
                ornek_veriler = [
                    ("Ahmet Yılmaz", "Kardiyoloji", "09:00,10:00,11:00,14:00"),
                    ("Ayşe Demir", "Kardiyoloji", "10:00,11:00,13:00,15:00"),
                    ("Mehmet Kaya", "Ortopedi", "09:00,13:00,14:00,16:00"),
                    ("Fatma Şahin", "Dahiliye", "09:00,10:00,11:00,12:00,14:00"),
                    ("Ali Can", "Göz Hastalıkları", "10:00,11:00,14:00,15:00"),
                    ("Zeynep Çelik", "KBB", "09:00,11:00,13:00,15:00"),
                    ("Burak Yılmaz", "Nöroloji", "10:00,11:00,14:00,16:00"),
                    ("Elif Öztürk", "Cildiye", "09:00,10:00,14:00,15:00"),
                    ("Caner Aslan", "Üroloji", "09:00,11:00,13:00,15:00"),
                    ("Gizem Yıldız", "Psikiyatri", "10:00,11:00,14:00,15:00"),
                    ("Oğuzhan Koç", "Diş Hekimliği", "09:00,10:00,13:00,14:00"),
                    ("Merve Nur", "Çocuk Sağlığı", "09:00,11:00,14:00,16:00"),
                    ("Kemal Sunal", "Genel Cerrahi", "10:00,14:00"),
                    ("Eda Ece", "Fizik Tedavi", "09:00,11:00,13:00,15:00"),
                    ("Büşra Pekin", "Beslenme ve Diyet", "10:00,11:00,14:00,15:00"),
                ]
                conn.executemany(
                    "INSERT INTO Doktorlar (ad, uzmanlik, uygun_saatler) VALUES (?, ?, ?)",
                    ornek_veriler
                )
                conn.commit()

    # ════════════════════════════════════════
    #  ADMİN CRUD
    # ════════════════════════════════════════

    def admin_dogrula(self, kullanici_adi: str, sifre: str) -> bool:
        """Admin kimlik doğrulama. Başarılıysa True döner."""
        with self._baglanti() as conn:
            row = conn.execute(
                "SELECT admin_id FROM Adminler WHERE kullanici_adi=? AND sifre_hash=?",
                (kullanici_adi, sifre_hashle(sifre)),
            ).fetchone()
        return row is not None

    # ════════════════════════════════════════
    #  DOKTOR CRUD
    # ════════════════════════════════════════

    def doktor_ekle(self, ad: str, uzmanlik: str, uygun_saatler: str, kullanici_adi: str, sifre: str) -> Optional[int]:
        """
        Yeni doktor kaydı oluşturur.

        Args:
            ad            : Doktorun adı soyadı.
            uzmanlik      : Uzmanlık alanı (örn: "Kardiyoloji").
            uygun_saatler : Virgülle ayrılmış saat dizisi (örn: "09:00,10:00").
            kullanici_adi : Giriş için kullanıcı adı.
            sifre         : Giriş şifresi.

        Returns:
            Yeni eklenen doktorun ID'si, hata (kullanıcı adı çakışması vs) varsa None.
        """
        try:
            with self._baglanti() as conn:
                cursor = conn.execute(
                    "INSERT INTO Doktorlar (ad, uzmanlik, uygun_saatler, kullanici_adi, sifre_hash) VALUES (?, ?, ?, ?, ?)",
                    (ad, uzmanlik, uygun_saatler, kullanici_adi, sifre_hashle(sifre)),
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def doktor_sil(self, doktor_id: int) -> bool:
        """
        Doktoru ve ilişkili tüm randevuları CASCADE ile siler.

        Returns:
            Silme işlemi gerçekleştiyse True.
        """
        with self._baglanti() as conn:
            cursor = conn.execute(
                "DELETE FROM Doktorlar WHERE doktor_id=?", (doktor_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def tum_doktorlar(self) -> list[dict]:
        """
        Tüm doktorları list-of-dict olarak döndürür.
        Bellekte hızlı filtreleme için dict yapısı kullanılır.
        """
        with self._baglanti() as conn:
            rows = conn.execute(
                "SELECT doktor_id, ad, uzmanlik, uygun_saatler, kullanici_adi FROM Doktorlar ORDER BY uzmanlik, ad"
            ).fetchall()
        return [dict(r) for r in rows]

    def doktor_getir(self, doktor_id: int) -> Optional[dict]:
        """ID'ye göre tek doktor döndürür."""
        with self._baglanti() as conn:
            row = conn.execute(
                "SELECT doktor_id, ad, uzmanlik, uygun_saatler, kullanici_adi FROM Doktorlar WHERE doktor_id=?",
                (doktor_id,),
            ).fetchone()
        return dict(row) if row else None

    def uzmanliga_gore_doktorlar(self, uzmanlik: str) -> list[dict]:
        """Belirli uzmanlık alanındaki doktorları döndürür."""
        with self._baglanti() as conn:
            rows = conn.execute(
                "SELECT doktor_id, ad, uzmanlik, uygun_saatler, kullanici_adi FROM Doktorlar WHERE uzmanlik=?",
                (uzmanlik,),
            ).fetchall()
        return [dict(r) for r in rows]

    def tum_uzmanliklar(self) -> list[str]:
        """Sistemdeki benzersiz uzmanlık alanlarını döndürür."""
        with self._baglanti() as conn:
            rows = conn.execute(
                "SELECT DISTINCT uzmanlik FROM Doktorlar ORDER BY uzmanlik"
            ).fetchall()
        return [r["uzmanlik"] for r in rows]

    def doktor_dogrula(self, kullanici_adi: str, sifre: str) -> Optional[dict]:
        """Doktor girişi için doğrulama yapar."""
        with self._baglanti() as conn:
            row = conn.execute(
                "SELECT doktor_id, ad, uzmanlik, uygun_saatler, kullanici_adi FROM Doktorlar WHERE kullanici_adi=? AND sifre_hash=?",
                (kullanici_adi, sifre_hashle(sifre)),
            ).fetchone()
        return dict(row) if row else None

    def doktorun_gunluk_randevulari(self, doktor_id: int, tarih: str) -> list[dict]:
        with self._baglanti() as conn:
            rows = conn.execute(
                """
                SELECT R.randevu_id, R.saat, H.ad AS hasta_adi, H.tc, R.durum
                FROM Randevular R
                JOIN Hastalar H ON R.hasta_id = H.hasta_id
                WHERE R.doktor_id = ? AND R.tarih = ?
                ORDER BY R.saat
                """,
                (doktor_id, tarih),
            ).fetchall()
        return [dict(r) for r in rows]

    def doktorun_haftalik_randevulari(self, doktor_id: int, baslangic_tarihi: str, bitis_tarihi: str) -> list[dict]:
        with self._baglanti() as conn:
            rows = conn.execute(
                """
                SELECT R.randevu_id, R.tarih, R.saat, H.ad AS hasta_adi, H.tc, R.durum
                FROM Randevular R
                JOIN Hastalar H ON R.hasta_id = H.hasta_id
                WHERE R.doktor_id = ? AND R.tarih BETWEEN ? AND ?
                ORDER BY R.tarih, R.saat
                """,
                (doktor_id, baslangic_tarihi, bitis_tarihi),
            ).fetchall()
        return [dict(r) for r in rows]

    # ════════════════════════════════════════
    #  HASTA CRUD
    # ════════════════════════════════════════

    def hasta_ekle(self, ad: str, tc: str, telefon: str, sifre: str) -> Optional[int]:
        """
        Yeni hasta kaydı oluşturur.

        Returns:
            Yeni hasta ID'si; TC/ad çakışması varsa None.
        """
        try:
            with self._baglanti() as conn:
                cursor = conn.execute(
                    "INSERT INTO Hastalar (ad, tc, telefon, sifre_hash) VALUES (?, ?, ?, ?)",
                    (ad, tc, telefon, sifre_hashle(sifre)),
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None   # Tekrar eden TC veya ad

    def hasta_dogrula(self, tc: str, sifre: str) -> Optional[dict]:
        """
        TC ve şifreyle hasta doğrulama.

        Returns:
            Hasta bilgilerini içeren dict; hata varsa None.
        """
        with self._baglanti() as conn:
            row = conn.execute(
                "SELECT hasta_id, ad, tc, telefon FROM Hastalar WHERE tc=? AND sifre_hash=?",
                (tc, sifre_hashle(sifre)),
            ).fetchone()
        return dict(row) if row else None

    def hasta_guncelle(self, hasta_id: int, yeni_ad: str, yeni_telefon: str) -> bool:
        """Hasta adı ve telefonunu günceller."""
        with self._baglanti() as conn:
            cursor = conn.execute(
                "UPDATE Hastalar SET ad=?, telefon=? WHERE hasta_id=?",
                (yeni_ad, yeni_telefon, hasta_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def tum_hastalar(self) -> list[dict]:
        """Tüm hastaları döndürür (admin görünümü)."""
        with self._baglanti() as conn:
            rows = conn.execute(
                "SELECT hasta_id, ad, tc, telefon FROM Hastalar ORDER BY ad"
            ).fetchall()
        return [dict(r) for r in rows]

    def hasta_sil(self, hasta_id: int) -> bool:
        """
        Hasta hesabını ve ilişkili tüm randevularını siler.
        Returns:
            Silme işlemi gerçekleştiyse True.
        """
        with self._baglanti() as conn:
            cursor = conn.execute(
                "DELETE FROM Hastalar WHERE hasta_id=?", (hasta_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    # ════════════════════════════════════════
    #  RANDEVU CRUD
    # ════════════════════════════════════════

    def randevu_ekle(
        self, tarih: str, saat: str, doktor_id: int, hasta_id: int
    ) -> Optional[int]:
        """
        Çakışma kontrolü yaparak randevu ekler.

        Returns:
            Yeni randevu ID'si; çakışma varsa None.
        """
        # Aynı doktor/tarih/saat dolu mu?
        with self._baglanti() as conn:
            mevcut = conn.execute(
                """
                SELECT randevu_id FROM Randevular
                WHERE doktor_id=? AND tarih=? AND saat=? AND durum='Aktif'
                """,
                (doktor_id, tarih, saat),
            ).fetchone()

            if mevcut:
                return None

            cursor = conn.execute(
                "INSERT INTO Randevular (tarih, saat, doktor_id, hasta_id) VALUES (?, ?, ?, ?)",
                (tarih, saat, doktor_id, hasta_id),
            )
            conn.commit()
            return cursor.lastrowid

    def randevu_iptal(self, randevu_id: int, hasta_id: Optional[int] = None) -> bool:
        """
        Randevuyu iptal eder.

        Args:
            randevu_id : İptal edilecek randevunun ID'si.
            hasta_id   : Verilirse yalnızca o hastanın randevusu iptal edilir
                         (güvenlik kontrolü). Admin çağrısı için None bırakın.

        Returns:
            Güncelleme yapıldıysa True.
        """
        sql = "UPDATE Randevular SET durum='İptal' WHERE randevu_id=? AND durum='Aktif'"
        params: tuple = (randevu_id,)

        if hasta_id is not None:
            sql += " AND hasta_id=?"
            params = (randevu_id, hasta_id)

        with self._baglanti() as conn:
            cursor = conn.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0

    def hasta_randevulari(self, hasta_id: int) -> list[dict]:
        """Belirli hastanın tüm randevularını döndürür."""
        with self._baglanti() as conn:
            rows = conn.execute(
                """
                SELECT R.randevu_id, R.tarih, R.saat,
                       D.ad AS doktor_adi, D.uzmanlik, R.durum
                FROM Randevular R
                JOIN Doktorlar D ON R.doktor_id = D.doktor_id
                WHERE R.hasta_id = ?
                ORDER BY R.tarih, R.saat
                """,
                (hasta_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def gunluk_randevular(self, tarih: str) -> list[dict]:
        """Belirtilen tarihteki tüm aktif randevuları döndürür."""
        with self._baglanti() as conn:
            rows = conn.execute(
                """
                SELECT R.randevu_id, R.saat,
                       D.ad AS doktor_adi, D.uzmanlik,
                       H.ad AS hasta_adi, H.tc,
                       R.durum
                FROM Randevular R
                JOIN Doktorlar D ON R.doktor_id = D.doktor_id
                JOIN Hastalar  H ON R.hasta_id  = H.hasta_id
                WHERE R.tarih = ?
                ORDER BY R.saat
                """,
                (tarih,),
            ).fetchall()
        return [dict(r) for r in rows]

    def dolu_saatler(self, doktor_id: int, tarih: str) -> list[str]:
        """
        Verilen doktor ve tarihteki dolu saatleri döndürür.
        Belleğe list olarak alınır; uygunluk kontrolünde set farkı alınır.
        """
        with self._baglanti() as conn:
            rows = conn.execute(
                """
                SELECT saat FROM Randevular
                WHERE doktor_id=? AND tarih=? AND durum='Aktif'
                """,
                (doktor_id, tarih),
            ).fetchall()
        return [r["saat"] for r in rows]
