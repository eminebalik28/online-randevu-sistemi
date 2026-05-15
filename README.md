# 🏥 Ala Randevu Sistemi (Hospital Appointment System)

![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-purple.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)
![Architecture](https://img.shields.io/badge/Architecture-OOP--Layered-success.svg)

Modern, karanlık/mor (Dark/Purple) temaya sahip, Python ve Tkinter kullanılarak geliştirilmiş masaüstü Hastane & Klinik Randevu Yönetim Sistemi. Nesne Yönelimli Programlama (OOP) ve Katmanlı Mimari (Layered Architecture) prensiplerine uygun olarak temiz ve sürdürülebilir bir yapıda kodlanmıştır.

## 📸 Ekran Görüntüleri
*(Buraya GitHub'a yüklerken projenin ekran görüntülerini ekleyebilirsiniz)*
<!--
![Giriş Ekranı](link_ekle)
![Hasta Paneli](link_ekle)
![Admin Paneli](link_ekle)
-->

## 🌟 Özellikler

### 🛡️ Yetkilendirme ve Güvenlik
* **Rol Tabanlı Erişim:** Admin, Doktor ve Hasta olmak üzere 3 farklı yetki seviyesi ve paneli.
* **Güvenli Şifreleme:** Tüm kullanıcı şifreleri veritabanında `SHA-256` ile hashlenerek (şifrelenerek) güvenle saklanır.

### ⚙️ Yönetici (Admin) Paneli
* **Doktor Yönetimi:** Yeni doktor ekleme, doktor silme ve uzmanlık alanları ile çalışma saatlerini belirleme.
* **Hasta Yönetimi:** Sistemdeki hastaları görüntüleme ve hesaplarını randevu çakışmalarını dikkate alarak silebilme.
* **Randevu Takibi:** Günlük ve genel tüm randevuları filtreleyip dinamik veri tabloları (Treeview) üzerinde inceleme.
* **Müdahale:** Gerektiğinde herhangi bir randevuyu idari olarak iptal edebilme.

### 👨‍⚕️ Doktor Paneli
* **Kişiselleştirilmiş Arayüz:** Doktorların sisteme özel girişi ile sadece kendi hastalarına erişimi.
* **Günlük Randevular:** O güne ait randevuları ve hasta bilgilerini saat sıralamasına göre listeleme.
* **Haftalık Randevular:** İleriye dönük 7 günlük detaylı randevu takvimi görüntüleme.

### 🩺 Hasta Paneli
* **Kayıt & Profil:** TC Kimlik Numarası ile güvenli kayıt olma. Ad, Soyad ve İletişim bilgilerini güncelleyebilme.
* **Dinamik Randevu Sistemi:** Uzmanlık Seçimi ➔ Doktor Seçimi ➔ Dinamik Tarih Seçimi ➔ Saat Seçimi adımlarını izleyerek müsaitlik durumuna göre anında randevu oluşturma.
* **Dashboard ve İstatistikler:** Modern bir "Bilgilerim" panosu üzerinde aktif randevu sayısını, toplam iptal/geçmiş istatistiklerini ve yaklaşan ilk randevu detaylarını görebilme.
* **Randevu Yönetimi:** Aktif randevuları görüntüleme ve istenilen randevuyu tek tıkla iptal etme.

## 🛠️ Mimari ve Teknolojiler

* **Programlama Dili:** Python 3.x
* **Arayüz (GUI):** Tkinter ve `ttk` kütüphaneleri (Klasik Tkinter görünümü yerine tamamen özelleştirilmiş Flat/Modern widget tasarımları kullanılmıştır).
* **Veritabanı:** SQLite3 (Veriler yerel olarak `randevu_sistemi.db` içerisinde saklanır, harici bir sunucu kurulumu gerektirmez).
* **Mimari:** GUI, Veritabanı (Data Access) ve İş Mantığı (Domain Models) birbirine sıkı sıkıya bağlı olmayan, modüler 3 katmanlı yapıda kurgulanmıştır.

## 🚀 Kurulum ve Çalıştırma

Proje standart kütüphaneler ile yazıldığından harici bir `pip` paketi kurulumu gerektirmez.

1. Depoyu bilgisayarınıza klonlayın (veya zip olarak indirin):
   ```bash
   git clone https://github.com/KULLANICI_ADINIZ/ala-randevu-sistemi.git
   cd "ala-randevu-sistemi"
   ```

2. Projeyi çalıştırın:
   ```bash
   python main.py
   ```

### 🔑 Varsayılan Yönetici (Admin) Girişi
Uygulama ilk çalıştırıldığında veritabanını (`randevu_sistemi.db`) ve varsayılan tabloları otomatik oluşturur. Hızlı test edebilmeniz için 15 adet örnek doktor verisi de eklenir.
* **Kullanıcı Adı:** `admin`
* **Şifre:** `admin123`

## 📂 Dosya ve Klasör Yapısı

* `main.py` : Uygulama giriş noktası (Entry Point). Veritabanını ve arayüzü birbirine bağlar.
* `gui.py` : Tkinter ekranları, widget yerleşimleri ve arayüz mantığı.
* `database.py` : SQLite bağlantısı, tablo kurulumları ve tüm CRUD operasyonlarını barındıran merkezi veritabanı sınıfı.
* `models.py` : Domain modelleri (`Hasta`, `Doktor`, `Randevu`) ve iş mantığını (Business Logic) kapsayan nesneler.
* `tema.py` : Sistemin merkezi renk paleti, widget stilleri (`ttk.Style`) ve arayüzü temiz tutan görsel yardımcı fonksiyonlar.

## 🤝 Katkıda Bulunma
Bu proje geliştirilmeye açıktır. Repoyu `fork` edip değişikliklerinizi yaparak `Pull Request` gönderebilirsiniz.

## 📄 Lisans
Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır. Dilediğiniz gibi kullanabilir, geliştirebilir ve paylaşabilirsiniz.
