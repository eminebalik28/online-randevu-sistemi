"""gui.py - Mor temalı Tkinter arayüz"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from typing import Optional, TYPE_CHECKING
import os, sys

PROJE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJE)

from tema import *
if TYPE_CHECKING:
    from database import DatabaseManager
    from models import Hasta, Doktor


class Uygulama(tk.Tk):
    def __init__(self, db: "DatabaseManager"):
        super().__init__()
        self._db = db
        self.title("🏥 Online Doktor Randevu Sistemi")
        self.geometry("1100x700")
        self.minsize(900, 600)
        stil_ayarla(self)
        self._ana = ttk.Frame(self)
        self._ana.pack(fill="both", expand=True)
        self.giris_ekrani()

    # ═══ GİRİŞ EKRANI ═══
    def giris_ekrani(self):
        temizle(self._ana)
        f = ttk.Frame(self._ana)
        f.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(f, text="🏥", font=("Segoe UI", 60)).pack(pady=(0,5))
        ttk.Label(f, text="Online Doktor Randevu", style="Title.TLabel").pack()
        ttk.Label(f, text="Sisteme giriş yapın veya kayıt olun", style="Sub.TLabel").pack(pady=(5,30))
        for txt, cmd in [("👤  Doktor / Admin Girişi", self._yetkili_dialog),
                         ("🩺  Hasta Girişi", self._hasta_dialog),
                         ("📝  Hasta Kaydı", self._kayit_dialog)]:
            b = ttk.Button(f, text=txt, style="Purple.TButton", command=cmd, width=25)
            b.pack(pady=6)
        ttk.Button(f, text="Çıkış", style="Card.TButton", command=self.destroy).pack(pady=(20,0))

    def _yetkili_dialog(self):
        temizle(self._ana)
        f = ttk.Frame(self._ana)
        f.place(relx=0.5, rely=0.5, anchor="center")
        cf = ttk.Frame(f, style="Card.TFrame", padding=(35, 30)); cf.pack(fill="both", expand=True)
        baslik_yaz(cf, "Doktor / Admin Girişi", "🔐", is_card=True)
        ku = form_alani(cf, "Kullanıcı Adı"); si = form_alani(cf, "Şifre", gizli=True)
        def giris():
            if self._db.admin_dogrula(ku.get(), si.get()):
                AdminPaneli(self._ana, self._db, self)
            else:
                doktor_veri = self._db.doktor_dogrula(ku.get(), si.get())
                if doktor_veri:
                    from models import Doktor
                    d = Doktor.db_den_yukle(doktor_veri["doktor_id"], self._db)
                    DoktorPaneli(self._ana, d, self._db, self)
                else:
                    mesaj_goster(cf, "Hatalı kullanıcı adı/şifre!", False)
        ttk.Button(cf, text="Giriş Yap", style="Purple.TButton", command=giris).pack(pady=(15, 5), fill="x")
        ttk.Button(cf, text="Geri", style="Card.TButton", command=self.giris_ekrani).pack(fill="x")

    def _hasta_dialog(self):
        from models import Hasta
        temizle(self._ana)
        f = ttk.Frame(self._ana)
        f.place(relx=0.5, rely=0.5, anchor="center")
        cf = ttk.Frame(f, style="Card.TFrame", padding=(35, 30)); cf.pack(fill="both", expand=True)
        baslik_yaz(cf, "Hasta Girişi", "🩺", is_card=True)
        tc = form_alani(cf, "TC Kimlik No"); si = form_alani(cf, "Şifre", gizli=True)
        def giris():
            h = Hasta.db_den_yukle(tc.get(), si.get(), self._db)
            if h:
                HastaPaneli(self._ana, h, self._db, self)
            else:
                mesaj_goster(cf, "TC veya şifre hatalı!", False)
        ttk.Button(cf, text="Giriş Yap", style="Purple.TButton", command=giris).pack(pady=(15, 5), fill="x")
        ttk.Button(cf, text="Geri", style="Card.TButton", command=self.giris_ekrani).pack(fill="x")

    def _kayit_dialog(self):
        from models import Hasta
        temizle(self._ana)
        f = ttk.Frame(self._ana)
        f.place(relx=0.5, rely=0.5, anchor="center")
        cf = ttk.Frame(f, style="Card.TFrame", padding=(35, 30)); cf.pack(fill="both", expand=True)
        baslik_yaz(cf, "Yeni Hasta Kaydı", "📝", is_card=True)
        ad = form_alani(cf, "Ad Soyad"); tc = form_alani(cf, "TC Kimlik No (11 hane)")
        tel = form_alani(cf, "Telefon"); si = form_alani(cf, "Şifre (min 4 kar.)", gizli=True)
        def kayit():
            h, m = Hasta.kayit_ol(ad.get(), tc.get(), tel.get(), si.get(), self._db)
            if h:
                mesaj_goster(cf, f"Kayıt başarılı! ID: {h.hasta_id}")
                self.after(2000, self.giris_ekrani)
            else:
                mesaj_goster(cf, m, False)
        ttk.Button(cf, text="Kayıt Ol", style="Purple.TButton", command=kayit).pack(pady=(15, 5), fill="x")
        ttk.Button(cf, text="Geri", style="Card.TButton", command=self.giris_ekrani).pack(fill="x")


class AdminPaneli:
    def __init__(self, ana, db, app):
        self._db = db; self._app = app
        temizle(ana); self._ana = ana
        # Sidebar
        self._side = ttk.Frame(ana, style="Card.TFrame", width=220)
        self._side.pack(side="left", fill="y")
        self._side.pack_propagate(False)
        ttk.Label(self._side, text="⚙️ Admin", style="Title.TLabel", background=CARD).pack(pady=20, padx=15)
        menu = [("📋 Doktor Ekle", self._doktor_ekle), ("👨‍⚕️ Doktorlar", self._doktor_listesi),
                ("👥 Hastalar", self._hasta_listesi), ("📅 Günlük Randevu", self._gunluk),
                ("📊 Tüm Randevular", self._tum_randevular), ("❌ Randevu İptal", self._randevu_iptal)]
        for txt, cmd in menu:
            ttk.Button(self._side, text=txt, style="Side.TButton", command=cmd).pack(fill="x", padx=8, pady=2)
        ttk.Button(self._side, text="🚪 Çıkış", style="Side.TButton", command=self._cikis).pack(fill="x", padx=8, pady=(20,2))
        # İçerik
        self._icerik = ttk.Frame(ana)
        self._icerik.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self._doktor_listesi()

    def _temizle(self):
        temizle(self._icerik)

    def _cikis(self):
        self._app.giris_ekrani()

    def _doktor_ekle(self):
        self._temizle()
        baslik_yaz(self._icerik, "Doktor Ekle", "📋")
        f = ttk.Frame(self._icerik, style="Card.TFrame"); f.pack(fill="x", padx=20, pady=10, ipadx=15, ipady=15)
        ad = form_alani(f, "Doktor Adı Soyadı"); uz = form_alani(f, "Uzmanlık Alanı")
        ka = form_alani(f, "Kullanıcı Adı"); si = form_alani(f, "Şifre", gizli=True)
        ttk.Label(f, text="Örnek: 09:00,10:00,11:00", style="Card.TLabel").pack(anchor="w")
        sa = form_alani(f, "Uygun Saatler (virgülle)")
        def ekle():
            if ad.get() and uz.get() and sa.get() and ka.get() and si.get():
                did = self._db.doktor_ekle(ad.get(), uz.get(), sa.get(), ka.get(), si.get())
                if did:
                    mesaj_goster(self._icerik, f"Dr. {ad.get()} eklendi! (ID: {did})")
                else:
                    mesaj_goster(self._icerik, "Kullanıcı adı sistemde mevcut!", False)
            else:
                mesaj_goster(self._icerik, "Tüm alanları doldurun!", False)
        ttk.Button(f, text="Ekle", style="Purple.TButton", command=ekle).pack(pady=15)

    def _doktor_listesi(self):
        self._temizle()
        baslik_yaz(self._icerik, "Doktor Listesi", "👨‍⚕️")
        doktorlar = self._db.tum_doktorlar()
        t = tablo_olustur(self._icerik, ("id","ad","uz","sa"), ("ID","Ad Soyad","Uzmanlık","Saatler"))
        for d in doktorlar:
            t.insert("", "end", values=(d["doktor_id"], d["ad"], d["uzmanlik"], d["uygun_saatler"]))
        
        f = ttk.Frame(self._icerik); f.pack(fill="x", pady=10)
        ttk.Label(f, text="Silinecek Doktor ID:").pack(side="left", padx=5)
        eid = ttk.Entry(f, width=10); eid.pack(side="left", padx=5)
        def sil():
            try:
                did = int(eid.get())
                if self._db.doktor_sil(did):
                    mesaj_goster(self._icerik, "Doktor silindi!")
                    self._doktor_listesi()
                else:
                    mesaj_goster(self._icerik, "Silinemedi!", False)
            except ValueError:
                mesaj_goster(self._icerik, "Geçersiz ID!", False)
        ttk.Button(f, text="Sil", style="Purple.TButton", command=sil).pack(side="left", padx=10)

    def _hasta_listesi(self):
        self._temizle()
        baslik_yaz(self._icerik, "Hasta Listesi", "👥")
        hastalar = self._db.tum_hastalar()
        t = tablo_olustur(self._icerik, ("id","ad","tc","tel"), ("ID","Ad Soyad","TC","Telefon"))
        for h in hastalar:
            t.insert("", "end", values=(h["hasta_id"], h["ad"], h["tc"], h["telefon"]))
        f = ttk.Frame(self._icerik); f.pack(fill="x", pady=10)
        ttk.Label(f, text="Silinecek Hasta ID:").pack(side="left", padx=5)
        eid = ttk.Entry(f, width=10); eid.pack(side="left", padx=5)
        def sil():
            try:
                hid = int(eid.get())
                randevular = self._db.hasta_randevulari(hid)
                if randevular:
                    cevap = messagebox.askyesno("Onay", "Bu hastanın geçmişte veya gelecekte kayıtlı randevuları var.\nYine de silmek istiyor musunuz?")
                    if not cevap:
                        return
                
                if self._db.hasta_sil(hid):
                    mesaj_goster(self._icerik, "Hasta silindi!")
                    self._hasta_listesi()
                else:
                    mesaj_goster(self._icerik, "Hasta bulunamadı!", False)
            except ValueError:
                mesaj_goster(self._icerik, "Geçersiz ID!", False)
        ttk.Button(f, text="Sil", style="Purple.TButton", command=sil).pack(side="left", padx=10)

    def _gunluk(self):
        self._temizle()
        baslik_yaz(self._icerik, "Günlük Randevular", "📅")
        f = ttk.Frame(self._icerik); f.pack(fill="x", pady=5)
        ttk.Label(f, text="Tarih (YYYY-MM-DD):").pack(side="left")
        te = ttk.Entry(f, width=15); te.insert(0, str(date.today())); te.pack(side="left", padx=5)
        rf = ttk.Frame(self._icerik)
        def ara():
            temizle(rf); rf.pack(fill="both", expand=True)
            randevular = self._db.gunluk_randevular(te.get())
            ttk.Label(rf, text=f"Toplam: {len(randevular)} randevu").pack(anchor="w", pady=5)
            t = tablo_olustur(rf, ("id","sa","dr","uz","ha","tc","du"), ("ID","Saat","Doktor","Uzmanlık","Hasta","TC","Durum"))
            for r in randevular:
                t.insert("", "end", values=(r["randevu_id"],r["saat"],r["doktor_adi"],r["uzmanlik"],r["hasta_adi"],r["tc"],r["durum"]))
        ttk.Button(f, text="Ara", style="Purple.TButton", command=ara).pack(side="left", padx=10)
        ara()

    def _tum_randevular(self):
        self._temizle()
        baslik_yaz(self._icerik, "Tüm Randevular", "📊")
        import sqlite3
        with sqlite3.connect(self._db.db_yolu) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""SELECT R.randevu_id, R.tarih, R.saat, D.ad AS doktor_adi, D.uzmanlik,
                H.ad AS hasta_adi, R.durum FROM Randevular R
                JOIN Doktorlar D ON R.doktor_id=D.doktor_id
                JOIN Hastalar H ON R.hasta_id=H.hasta_id ORDER BY R.tarih,R.saat""").fetchall()
        t = tablo_olustur(self._icerik, ("id","ta","sa","dr","uz","ha","du"), ("ID","Tarih","Saat","Doktor","Uzmanlık","Hasta","Durum"))
        for r in rows:
            t.insert("", "end", values=(r["randevu_id"],r["tarih"],r["saat"],r["doktor_adi"],r["uzmanlik"],r["hasta_adi"],r["durum"]))

    def _randevu_iptal(self):
        self._temizle()
        baslik_yaz(self._icerik, "Randevu İptal", "❌")
        self._tum_randevular_goster()
        f = ttk.Frame(self._icerik); f.pack(fill="x", pady=10)
        ttk.Label(f, text="İptal edilecek ID:").pack(side="left")
        eid = ttk.Entry(f, width=10); eid.pack(side="left", padx=5)
        def iptal():
            try:
                rid = int(eid.get())
                if self._db.randevu_iptal(rid, hasta_id=None):
                    mesaj_goster(self._icerik, f"Randevu #{rid} iptal edildi!")
                else:
                    mesaj_goster(self._icerik, "Bulunamadı veya zaten iptal!", False)
            except ValueError:
                mesaj_goster(self._icerik, "Geçersiz ID!", False)
        ttk.Button(f, text="İptal Et", style="Purple.TButton", command=iptal).pack(side="left", padx=10)

    def _tum_randevular_goster(self):
        import sqlite3
        with sqlite3.connect(self._db.db_yolu) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""SELECT R.randevu_id, R.tarih, R.saat, D.ad AS doktor_adi, D.uzmanlik,
                H.ad AS hasta_adi, R.durum FROM Randevular R
                JOIN Doktorlar D ON R.doktor_id=D.doktor_id
                JOIN Hastalar H ON R.hasta_id=H.hasta_id ORDER BY R.tarih,R.saat""").fetchall()
        t = tablo_olustur(self._icerik, ("id","ta","sa","dr","uz","ha","du"), ("ID","Tarih","Saat","Doktor","Uzmanlık","Hasta","Durum"))
        for r in rows:
            t.insert("", "end", values=(r["randevu_id"],r["tarih"],r["saat"],r["doktor_adi"],r["uzmanlik"],r["hasta_adi"],r["durum"]))


class HastaPaneli:
    def __init__(self, ana, hasta, db, app):
        self._hasta = hasta; self._db = db; self._app = app
        temizle(ana); self._ana = ana
        self._side = ttk.Frame(ana, style="Card.TFrame", width=220)
        self._side.pack(side="left", fill="y"); self._side.pack_propagate(False)
        ttk.Label(self._side, text=f"👤 {hasta.ad}", style="Title.TLabel", background=CARD, font=("Segoe UI",14,"bold")).pack(pady=20, padx=10)
        menu = [("📋 Bilgilerim", self._bilgiler), ("✏️ Güncelle", self._guncelle),
                ("🗓️ Randevu Al", self._randevu_al), ("📅 Randevularım", self._randevularim),
                ("❌ Randevu İptal", self._randevu_iptal)]
        for txt, cmd in menu:
            ttk.Button(self._side, text=txt, style="Side.TButton", command=cmd).pack(fill="x", padx=8, pady=2)
        ttk.Button(self._side, text="🚪 Çıkış", style="Side.TButton", command=self._cikis).pack(fill="x", padx=8, pady=(20,2))
        self._icerik = ttk.Frame(ana)
        self._icerik.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self._bilgiler()

    def _temizle(self):
        temizle(self._icerik)

    def _cikis(self):
        self._app.giris_ekrani()

    def _bilgiler(self):
        self._temizle()
        baslik_yaz(self._icerik, "Bilgi Kartım ve İstatistikler", "📋")
        
        # Üst Kısım - İki Sütunlu Yapı
        ust_frame = ttk.Frame(self._icerik)
        ust_frame.pack(fill="x", padx=20, pady=10)
        
        # Sol Taraf: Profil Kartı
        sol_frame = ttk.Frame(ust_frame, style="Card.TFrame")
        sol_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), ipadx=20, ipady=20)
        
        # Profil İkonu
        ttk.Label(sol_frame, text="👤", font=("Segoe UI", 48), background=CARD).pack(pady=(0, 10))
        ttk.Label(sol_frame, text=self._hasta.ad, font=("Segoe UI", 16, "bold"), background=CARD, foreground=PURPLE_LIGHT).pack()
        ttk.Label(sol_frame, text="Hasta Hesabı", font=("Segoe UI", 10), background=CARD, foreground=GRAY).pack(pady=(0, 15))
        
        # Çizgi
        tk.Frame(sol_frame, bg=PURPLE, height=1).pack(fill="x", padx=20, pady=10)
        
        # Kişisel Bilgiler
        bilgiler = self._hasta.bilgilerimi_goster()
        gosterilecekler = {
            "TC Kimlik": "🆔",
            "Telefon": "📱",
            "Hasta ID": "🔖",
        }
        
        for k, ikon in gosterilecekler.items():
            v = bilgiler.get(k, "-")
            satir = ttk.Frame(sol_frame, style="Card.TFrame")
            satir.pack(fill="x", padx=20, pady=5)
            ttk.Label(satir, text=f"{ikon} {k}:", style="Card.TLabel", font=FONT_B, width=12).pack(side="left")
            ttk.Label(satir, text=str(v), style="Card.TLabel").pack(side="left", padx=10)
            
        # Sağ Taraf: İstatistikler ve Durum
        sag_frame = ttk.Frame(ust_frame)
        sag_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Randevu Verilerini Al
        tum_randevular = self._hasta.randevularimi_getir()
        aktif_randevular = [r for r in tum_randevular if r["durum"] == "Aktif"]
        iptal_randevular = [r for r in tum_randevular if r["durum"] == "İptal"]
        
        # Aktif Randevu Kartı
        stat1 = ttk.Frame(sag_frame, style="Card.TFrame")
        stat1.pack(fill="both", expand=True, pady=(0, 10))
        
        stat1_ic = ttk.Frame(stat1, style="Card.TFrame")
        stat1_ic.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(stat1_ic, text="📅 Aktif Randevular", font=("Segoe UI", 14, "bold"), background=CARD, foreground=WHITE).pack()
        ttk.Label(stat1_ic, text=str(len(aktif_randevular)), font=("Segoe UI", 36, "bold"), background=CARD, foreground=GREEN).pack(pady=(5,0))
        
        # Toplam/İptal İstatistik Kartı
        stat2 = ttk.Frame(sag_frame, style="Card.TFrame")
        stat2.pack(fill="both", expand=True, pady=(10, 0))
        
        stat2_ic = ttk.Frame(stat2, style="Card.TFrame")
        stat2_ic.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(stat2_ic, text="📊 Randevu Geçmişi", font=("Segoe UI", 14, "bold"), background=CARD, foreground=WHITE).pack()
        ttk.Label(stat2_ic, text=f"Toplam: {len(tum_randevular)}   |   İptal Edilen: {len(iptal_randevular)}", font=("Segoe UI", 12), background=CARD, foreground=GRAY).pack(pady=(10,0))
        
        # Alt Kısım - Yaklaşan Randevu veya Uyarı
        alt_frame = ttk.Frame(self._icerik, style="Card.TFrame")
        alt_frame.pack(fill="x", padx=20, pady=10, ipadx=15, ipady=15)
        
        if aktif_randevular:
            yaklasan = aktif_randevular[0]
            ttk.Label(alt_frame, text="🔔 Yaklaşan Randevunuz", font=("Segoe UI", 12, "bold"), background=CARD, foreground=PURPLE_LIGHT).pack(anchor="center")
            bilgi_metni = f"Dr. {yaklasan['doktor_adi']} ({yaklasan['uzmanlik']}) — Tarih: {yaklasan['tarih']} | Saat: {yaklasan['saat']}"
            ttk.Label(alt_frame, text=bilgi_metni, font=FONT, background=CARD, foreground=WHITE).pack(anchor="center", pady=(5,0))
        else:
            ttk.Label(alt_frame, text="ℹ️ Yaklaşan aktif bir randevunuz bulunmamaktadır.", font=("Segoe UI", 11, "italic"), background=CARD, foreground=GRAY).pack(anchor="center")

    def _guncelle(self):
        self._temizle()
        baslik_yaz(self._icerik, "Bilgileri Güncelle", "✏️")
        f = ttk.Frame(self._icerik, style="Card.TFrame"); f.pack(fill="x", padx=20, pady=10, ipadx=15, ipady=15)
        ad = form_alani(f, f"Ad Soyad [{self._hasta.ad}]")
        tel = form_alani(f, f"Telefon [{self._hasta.telefon}]")
        def guncelle():
            ok, m = self._hasta.bilgileri_guncelle(ad.get(), tel.get())
            mesaj_goster(self._icerik, m, ok)
        ttk.Button(f, text="Güncelle", style="Purple.TButton", command=guncelle).pack(pady=15)

    def _randevu_al(self):
        from models import Doktor
        self._temizle()
        baslik_yaz(self._icerik, "Randevu Al", "🗓️")
        uzmanliklar = self._db.tum_uzmanliklar()
        if not uzmanliklar:
            ttk.Label(self._icerik, text="Sistemde doktor yok!").pack(); return
        # Adım 1: Uzmanlık
        ttk.Label(self._icerik, text="Adım 1: Uzmanlık Seçin", font=FONT_B).pack(anchor="w", pady=5)
        uf = ttk.Frame(self._icerik); uf.pack(fill="both", expand=True, pady=5)
        
        IKONLAR = {
            "Ortopedi": "🦴", "Kardiyoloji": "❤️", "Dahiliye": "🩺", "Göz Hastalıkları": "👁️",
            "KBB": "👂", "Nöroloji": "🧠", "Cildiye": "✨", "Üroloji": "💧", "Psikiyatri": "🛋️",
            "Diş Hekimliği": "🦷", "Çocuk Sağlığı": "👶", "Genel Cerrahi": "⚕️",
            "Fizik Tedavi": "💪", "Beslenme ve Diyet": "🍏"
        }
        
        satir = 0
        sutun = 0
        for u in uzmanliklar:
            ikon = IKONLAR.get(u, "🏥")
            btn = ttk.Button(uf, text=f"{ikon}  {u}", style="Card.TButton",
                             command=lambda uz=u: self._adim2(uz))
            btn.grid(row=satir, column=sutun, padx=8, pady=8, sticky="ew")
            uf.columnconfigure(sutun, weight=1)
            sutun += 1
            if sutun > 2: # 3 sütun olunca alt satıra in
                sutun = 0
                satir += 1

    def _adim2(self, uzmanlik):
        from models import Doktor
        self._temizle()
        baslik_yaz(self._icerik, f"Randevu Al — {uzmanlik}", "🗓️")
        doktorlar = self._db.uzmanliga_gore_doktorlar(uzmanlik)
        ttk.Label(self._icerik, text="Adım 2: Doktor Seçin", font=FONT_B).pack(anchor="w", pady=5)
        for d in doktorlar:
            nesne = Doktor(d["doktor_id"], d["ad"], d["uzmanlik"], d["uygun_saatler"], self._db)
            ttk.Button(self._icerik, text=f"Dr. {nesne.ad}  ({nesne.uygun_saatler})", style="Card.TButton",
                       command=lambda n=nesne: self._adim3(n)).pack(fill="x", padx=20, pady=3)

    def _adim3(self, doktor):
        self._temizle()
        baslik_yaz(self._icerik, f"Dr. {doktor.ad}", "🗓️")
        f = ttk.Frame(self._icerik, style="Card.TFrame"); f.pack(fill="x", padx=20, pady=10, ipadx=15, ipady=15)
        
        ttk.Label(f, text="Adım 3: Tarih Seçin", font=FONT_B, style="Card.TLabel").pack(anchor="w", pady=5)
        tarih_frame = ttk.Frame(f, style="Card.TFrame")
        tarih_frame.pack(anchor="w", pady=5)
        
        bugun = date.today()
        gun_cb = ttk.Combobox(tarih_frame, values=[f"{i:02d}" for i in range(1, 32)], width=4, state="readonly")
        gun_cb.set(bugun.strftime("%d"))
        gun_cb.pack(side="left", padx=2)
        ttk.Label(tarih_frame, text=".", style="Card.TLabel").pack(side="left")
        
        ay_cb = ttk.Combobox(tarih_frame, values=[f"{i:02d}" for i in range(1, 13)], width=4, state="readonly")
        ay_cb.set(bugun.strftime("%m"))
        ay_cb.pack(side="left", padx=2)
        ttk.Label(tarih_frame, text=".", style="Card.TLabel").pack(side="left")
        
        yil_cb = ttk.Combobox(tarih_frame, values=[str(bugun.year), str(bugun.year + 1)], width=6, state="readonly")
        yil_cb.set(bugun.strftime("%Y"))
        yil_cb.pack(side="left", padx=2)

        sf = ttk.Frame(self._icerik)
        def saatleri_goster():
            temizle(sf); sf.pack(fill="x", pady=10)
            secilen_tarih = f"{yil_cb.get()}-{ay_cb.get()}-{gun_cb.get()}"
            gosterim_tarihi = f"{gun_cb.get()}.{ay_cb.get()}.{yil_cb.get()}"
            
            musait = doktor.musait_saatler(secilen_tarih)
            if not musait:
                ttk.Label(sf, text=f"{gosterim_tarihi} tarihinde müsait saat yok!").pack(); return
            ttk.Label(sf, text=f"Adım 4: Saat Seçin ({gosterim_tarihi})", font=FONT_B).pack(anchor="w", pady=5)
            bf = ttk.Frame(sf); bf.pack(fill="x")
            for s in musait:
                ttk.Button(bf, text=s, style="Card.TButton",
                           command=lambda sa=s, t=secilen_tarih: self._randevu_onayla(doktor, t, sa)).pack(side="left", padx=3, pady=3)
        ttk.Button(f, text="Saatleri Göster", style="Purple.TButton", command=saatleri_goster).pack(pady=10, anchor="w")

    def _randevu_onayla(self, doktor, tarih, saat):
        ok, m = self._hasta.randevu_al(doktor, tarih, saat)
        if ok:
            messagebox.showinfo("Başarılı", m)
        else:
            messagebox.showerror("Hata", m)
        self._randevularim()

    def _randevularim(self):
        self._temizle()
        baslik_yaz(self._icerik, "Randevularım", "📅")
        randevular = self._hasta.randevularimi_getir()
        t = tablo_olustur(self._icerik, ("id","ta","sa","dr","uz","du"), ("ID","Tarih","Saat","Doktor","Uzmanlık","Durum"))
        for r in randevular:
            t.insert("", "end", values=(r["randevu_id"],r["tarih"],r["saat"],r["doktor_adi"],r["uzmanlik"],r["durum"]))

    def _randevu_iptal(self):
        self._temizle()
        baslik_yaz(self._icerik, "Randevu İptal", "❌")
        randevular = self._hasta.randevularimi_getir()
        t = tablo_olustur(self._icerik, ("id","ta","sa","dr","uz","du"), ("ID","Tarih","Saat","Doktor","Uzmanlık","Durum"))
        for r in randevular:
            t.insert("", "end", values=(r["randevu_id"],r["tarih"],r["saat"],r["doktor_adi"],r["uzmanlik"],r["durum"]))
        f = ttk.Frame(self._icerik); f.pack(fill="x", pady=10)
        ttk.Label(f, text="İptal edilecek ID:").pack(side="left")
        eid = ttk.Entry(f, width=10); eid.pack(side="left", padx=5)
        def iptal():
            try:
                rid = int(eid.get())
                ok, m = self._hasta.randevu_iptal_et(rid)
                mesaj_goster(self._icerik, m, ok)
                if ok: self._randevu_iptal()
            except ValueError:
                mesaj_goster(self._icerik, "Geçersiz ID!", False)
        ttk.Button(f, text="İptal Et", style="Purple.TButton", command=iptal).pack(side="left", padx=10)


class DoktorPaneli:
    def __init__(self, ana, doktor, db, app):
        self._doktor = doktor; self._db = db; self._app = app
        temizle(ana); self._ana = ana
        self._side = ttk.Frame(ana, style="Card.TFrame", width=220)
        self._side.pack(side="left", fill="y"); self._side.pack_propagate(False)
        ttk.Label(self._side, text=f"👨‍⚕️ Dr. {doktor.ad}", style="Title.TLabel", background=CARD, font=("Segoe UI",12,"bold")).pack(pady=20, padx=10)
        menu = [("📅 Günlük Randevular", self._gunluk), ("📊 Haftalık Randevular", self._haftalik)]
        for txt, cmd in menu:
            ttk.Button(self._side, text=txt, style="Side.TButton", command=cmd).pack(fill="x", padx=8, pady=2)
        ttk.Button(self._side, text="🚪 Çıkış", style="Side.TButton", command=self._cikis).pack(fill="x", padx=8, pady=(20,2))
        self._icerik = ttk.Frame(ana)
        self._icerik.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self._gunluk()

    def _temizle(self):
        temizle(self._icerik)

    def _cikis(self):
        self._app.giris_ekrani()

    def _gunluk(self):
        self._temizle()
        baslik_yaz(self._icerik, "Günlük Randevularım", "📅")
        bugun = str(date.today())
        ttk.Label(self._icerik, text=f"Tarih: {bugun}", font=("Segoe UI", 12)).pack(anchor="w", pady=5)
        randevular = self._db.doktorun_gunluk_randevulari(self._doktor.doktor_id, bugun)
        t = tablo_olustur(self._icerik, ("id","sa","ha","tc","du"), ("ID","Saat","Hasta","TC","Durum"))
        for r in randevular:
            t.insert("", "end", values=(r["randevu_id"], r["saat"], r["hasta_adi"], r["tc"], r["durum"]))

    def _haftalik(self):
        self._temizle()
        baslik_yaz(self._icerik, "Haftalık Randevularım", "📊")
        from datetime import timedelta
        bugun = date.today()
        haftaya = bugun + timedelta(days=7)
        ttk.Label(self._icerik, text=f"Tarih Aralığı: {bugun} - {haftaya}", font=("Segoe UI", 12)).pack(anchor="w", pady=5)
        randevular = self._db.doktorun_haftalik_randevulari(self._doktor.doktor_id, str(bugun), str(haftaya))
        t = tablo_olustur(self._icerik, ("id","ta","sa","ha","tc","du"), ("ID","Tarih","Saat","Hasta","TC","Durum"))
        for r in randevular:
            t.insert("", "end", values=(r["randevu_id"], r["tarih"], r["saat"], r["hasta_adi"], r["tc"], r["durum"]))
