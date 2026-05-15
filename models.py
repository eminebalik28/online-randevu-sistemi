"""
models.py
─────────
OOP prensipleriyle tanımlanmış Hasta, Doktor ve Randevu
sınıfları. İş mantığı burada, kalıcı depolama database.py'de.
"""

from __future__ import annotations
from datetime import date, datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from database import DatabaseManager


# ────────────────────────────────────────────
#  TEMEL SOYUT SINIF
# ────────────────────────────────────────────

class KayitliVarlik:
    """
    Tüm domain sınıflarının miras aldığı taban sınıf.
    Ortak id/str/repr davranışlarını sağlar.
    """

    def __init__(self, id_: int):
        self._id = id_

    @property
    def id(self) -> int:
        return self._id

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id}>"


# ════════════════════════════════════════════
#  HASTA SINIFI
# ════════════════════════════════════════════

class Hasta(KayitliVarlik):
    """
    Hasta domain sınıfı.

    Attributes:
        hasta_id (int)   : Veritabanı birincil anahtarı.
        ad       (str)   : Ad soyad.
        tc       (str)   : TC kimlik numarası (11 hane).
        telefon  (str)   : İletişim numarası.
    """

    def __init__(
        self,
        hasta_id: int,
        ad: str,
        tc: str,
        telefon: str,
        db: "DatabaseManager",
    ):
        super().__init__(hasta_id)
        self.hasta_id = hasta_id
        self.ad       = ad
        self.tc       = tc
        self.telefon  = telefon
        self._db      = db

    # ── BİLGİ GÖSTER ─────────────────────────

    def bilgilerimi_goster(self) -> dict:
        """
        Hasta bilgilerini dict olarak döndürür.
        GUI katmanı bu dict'i istediği gibi biçimlendirir.
        """
        return {
            "Hasta ID" : self.hasta_id,
            "Ad Soyad" : self.ad,
            "TC Kimlik": self.tc,
            "Telefon"  : self.telefon,
        }

    # ── RANDEVU AL ────────────────────────────

    def randevu_al(
        self,
        doktor: "Doktor",
        tarih: str,
        saat: str,
    ) -> tuple[bool, str]:
        """
        Belirtilen doktor, tarih ve saatte randevu oluşturur.

        Args:
            doktor : Randevu alınacak Doktor nesnesi.
            tarih  : YYYY-MM-DD formatında tarih.
            saat   : HH:MM formatında saat.

        Returns:
            (başarı: bool, mesaj: str) demeti.
        """
        # Tarih geçmiş mi?
        try:
            randevu_tarihi = datetime.strptime(tarih, "%Y-%m-%d").date()
        except ValueError:
            return False, "Geçersiz tarih formatı. YYYY-MM-DD kullanın."

        if randevu_tarihi < date.today():
            return False, "Geçmiş bir tarihe randevu alınamaz."

        # Doktor uygunluk kontrolü
        uygun, hata = doktor.uygunluk_kontrol(tarih, saat)
        if not uygun:
            return False, hata

        # Veritabanına kaydet
        rid = self._db.randevu_ekle(tarih, saat, doktor.doktor_id, self.hasta_id)
        if rid is None:
            return False, "Bu saat zaten dolu. Lütfen başka bir saat seçin."

        return True, f"Randevu oluşturuldu. (ID: {rid})"

    # ── BİLGİ GÜNCELLE ───────────────────────

    def bilgileri_guncelle(self, yeni_ad: str, yeni_telefon: str) -> tuple[bool, str]:
        """
        Ad ve telefonu hem nesnede hem veritabanında günceller.

        Returns:
            (başarı: bool, mesaj: str) demeti.
        """
        yeni_ad      = yeni_ad.strip()      or self.ad
        yeni_telefon = yeni_telefon.strip() or self.telefon

        if self._db.hasta_guncelle(self.hasta_id, yeni_ad, yeni_telefon):
            self.ad      = yeni_ad
            self.telefon = yeni_telefon
            return True, "Bilgiler başarıyla güncellendi."
        return False, "Güncelleme sırasında bir hata oluştu."

    # ── RANDEVULARIM ──────────────────────────

    def randevularimi_getir(self) -> list[dict]:
        """
        Hastanın tüm randevularını döndürür.
        Her eleman bir dict; GUI katmanı tablo olarak gösterir.
        """
        return self._db.hasta_randevulari(self.hasta_id)

    # ── RANDEVU İPTAL ────────────────────────

    def randevu_iptal_et(self, randevu_id: int) -> tuple[bool, str]:
        """
        Kendi randevusunu iptal eder.
        Güvenlik: Yalnızca bu hastaya ait randevu iptal edilebilir.

        Returns:
            (başarı: bool, mesaj: str) demeti.
        """
        basari = self._db.randevu_iptal(randevu_id, hasta_id=self.hasta_id)
        if basari:
            return True, f"Randevu (ID: {randevu_id}) başarıyla iptal edildi."
        return False, "Randevu bulunamadı veya zaten iptal edilmiş."

    # ── FACTORY ──────────────────────────────

    @classmethod
    def db_den_yukle(cls, tc: str, sifre: str, db: "DatabaseManager") -> Optional["Hasta"]:
        """TC ve şifreyle veritabanından Hasta nesnesi döndürür."""
        veri = db.hasta_dogrula(tc, sifre)
        if not veri:
            return None
        return cls(
            hasta_id=veri["hasta_id"],
            ad=veri["ad"],
            tc=veri["tc"],
            telefon=veri["telefon"],
            db=db,
        )

    @classmethod
    def kayit_ol(
        cls, ad: str, tc: str, telefon: str, sifre: str, db: "DatabaseManager"
    ) -> tuple[Optional["Hasta"], str]:
        """
        Yeni hasta kaydı oluşturur ve nesneyi döndürür.

        Returns:
            (Hasta nesnesi veya None, mesaj) demeti.
        """
        if not tc.isdigit() or len(tc) != 11:
            return None, "TC kimlik numarası 11 haneli olmalıdır."
        if len(sifre) < 4:
            return None, "Şifre en az 4 karakter olmalıdır."

        hid = db.hasta_ekle(ad.strip(), tc, telefon.strip(), sifre)
        if hid is None:
            return None, "Bu TC kimlik numarası veya kullanıcı adı zaten kayıtlı."

        return (
            cls(hasta_id=hid, ad=ad.strip(), tc=tc, telefon=telefon.strip(), db=db),
            "Kayıt başarılı.",
        )

    def __str__(self) -> str:
        return f"{self.ad} (TC: {self.tc})"


# ════════════════════════════════════════════
#  DOKTOR SINIFI
# ════════════════════════════════════════════

class Doktor(KayitliVarlik):
    """
    Doktor domain sınıfı.

    Attributes:
        doktor_id     (int) : Veritabanı birincil anahtarı.
        ad            (str) : Ad soyad.
        uzmanlik      (str) : Uzmanlık alanı.
        uygun_saatler (str) : Virgülle ayrılmış saat dizisi.
    """

    def __init__(
        self,
        doktor_id: int,
        ad: str,
        uzmanlik: str,
        uygun_saatler: str,
        db: "DatabaseManager",
        kullanici_adi: str = "",
    ):
        super().__init__(doktor_id)
        self.doktor_id     = doktor_id
        self.ad            = ad
        self.uzmanlik      = uzmanlik
        self.uygun_saatler = uygun_saatler   # "09:00,10:00,11:00"
        self.kullanici_adi = kullanici_adi
        self._db           = db

    # ── SAAT LİSTESİ ─────────────────────────

    @property
    def saat_listesi(self) -> list[str]:
        """Uygun saatleri Python listesi olarak döndürür."""
        return [s.strip() for s in self.uygun_saatler.split(",") if s.strip()]

    # ── UYGUNLUK KONTROL ─────────────────────

    def uygunluk_kontrol(self, tarih: str, saat: str) -> tuple[bool, str]:
        """
        Belirli tarih ve saatin müsait olup olmadığını denetler.

        Kontrol adımları:
          1. Saat, tanımlı çalışma saatleri içinde mi?
          2. Veritabanında çakışan aktif randevu var mı?

        Returns:
            (uygun: bool, mesaj: str) demeti.
        """
        if saat not in self.saat_listesi:
            return False, f"'{saat}' bu doktorun çalışma saatlerinde değil."

        dolu = self._db.dolu_saatler(self.doktor_id, tarih)
        if saat in dolu:
            return False, f"{saat} saati dolu. Lütfen başka bir saat seçin."

        return True, "Saat müsait."

    # ── MÜSAİT SAATLER ───────────────────────

    def musait_saatler(self, tarih: str) -> list[str]:
        """
        Belirli tarihte randevu alınabilecek saatleri döndürür.
        Dolu saatler, tüm saatler kümesinden çıkarılır.
        """
        dolu_set = set(self._db.dolu_saatler(self.doktor_id, tarih))
        return [s for s in self.saat_listesi if s not in dolu_set]

    # ── FACTORY ──────────────────────────────

    @classmethod
    def db_den_yukle(cls, doktor_id: int, db: "DatabaseManager") -> Optional["Doktor"]:
        """ID'ye göre veritabanından Doktor nesnesi döndürür."""
        veri = db.doktor_getir(doktor_id)
        if not veri:
            return None
        return cls(
            doktor_id=veri["doktor_id"],
            ad=veri["ad"],
            uzmanlik=veri["uzmanlik"],
            uygun_saatler=veri["uygun_saatler"],
            db=db,
            kullanici_adi=veri.get("kullanici_adi", ""),
        )

    @classmethod
    def tum_doktor_nesneleri(cls, db: "DatabaseManager") -> list["Doktor"]:
        """Veritabanındaki tüm doktorları Doktor nesneleri olarak döndürür."""
        return [
            cls(
                doktor_id=d["doktor_id"],
                ad=d["ad"],
                uzmanlik=d["uzmanlik"],
                uygun_saatler=d["uygun_saatler"],
                db=db,
                kullanici_adi=d.get("kullanici_adi", ""),
            )
            for d in db.tum_doktorlar()
        ]

    def __str__(self) -> str:
        return f"Dr. {self.ad} — {self.uzmanlik}"


# ════════════════════════════════════════════
#  RANDEVU SINIFI
# ════════════════════════════════════════════

class Randevu(KayitliVarlik):
    """
    Randevu domain sınıfı.

    Attributes:
        randevu_id (int) : Birincil anahtar.
        tarih      (str) : YYYY-MM-DD.
        saat       (str) : HH:MM.
        doktor     (str) : Doktor adı (JOIN'den gelir).
        hasta      (str) : Hasta adı  (JOIN'den gelir).
        durum      (str) : 'Aktif' veya 'İptal'.
    """

    def __init__(
        self,
        randevu_id: int,
        tarih: str,
        saat: str,
        doktor_adi: str,
        hasta_adi: str,
        uzmanlik: str,
        durum: str,
        db: "DatabaseManager",
    ):
        super().__init__(randevu_id)
        self.randevu_id = randevu_id
        self.tarih      = tarih
        self.saat       = saat
        self.doktor     = doktor_adi
        self.hasta      = hasta_adi
        self.uzmanlik   = uzmanlik
        self.durum      = durum
        self._db        = db

    # ── RANDEVU OLUSTUR (statik fabrika) ─────

    @staticmethod
    def randevu_olustur(
        hasta_nesnesi: Hasta,
        doktor_nesnesi: Doktor,
        tarih: str,
        saat: str,
    ) -> tuple[bool, str]:
        """
        Hasta nesnesi üzerinden randevu oluşturur.
        Tüm iş mantığı Hasta.randevu_al() metoduna delege edilir.

        Returns:
            (başarı: bool, mesaj: str) demeti.
        """
        return hasta_nesnesi.randevu_al(doktor_nesnesi, tarih, saat)

    # ── RANDEVU İPTAL ────────────────────────

    def randevu_iptal(self, hasta_id: Optional[int] = None) -> tuple[bool, str]:
        """
        Mevcut randevuyu iptal eder.

        Args:
            hasta_id : Admin işlemleri için None; hasta işlemleri için hasta ID'si.

        Returns:
            (başarı: bool, mesaj: str) demeti.
        """
        if self.durum == "İptal":
            return False, "Bu randevu zaten iptal edilmiş."

        basari = self._db.randevu_iptal(self.randevu_id, hasta_id)
        if basari:
            self.durum = "İptal"
            return True, f"Randevu #{self.randevu_id} iptal edildi."
        return False, "İptal işlemi başarısız. Yetki hatası olabilir."

    # ── OZET ─────────────────────────────────

    def ozet(self) -> dict:
        """Randevu bilgilerini dict olarak döndürür."""
        return {
            "ID"      : self.randevu_id,
            "Tarih"   : self.tarih,
            "Saat"    : self.saat,
            "Doktor"  : self.doktor,
            "Uzmanlik": self.uzmanlik,
            "Hasta"   : self.hasta,
            "Durum"   : self.durum,
        }

    # ── FACTORY ──────────────────────────────

    @classmethod
    def listeden_olustur(cls, veri: dict, db: "DatabaseManager") -> "Randevu":
        """Veritabanı dict'inden Randevu nesnesi oluşturur."""
        return cls(
            randevu_id=veri["randevu_id"],
            tarih=veri["tarih"],
            saat=veri["saat"],
            doktor_adi=veri.get("doktor_adi", ""),
            hasta_adi=veri.get("hasta_adi", ""),
            uzmanlik=veri.get("uzmanlik", ""),
            durum=veri["durum"],
            db=db,
        )

    def __str__(self) -> str:
        return f"[{self.durum}] {self.tarih} {self.saat} — {self.doktor} / {self.hasta}"
