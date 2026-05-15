"""tema.py - Mor tema sabitleri ve yardımcı widget'lar"""
import tkinter as tk
from tkinter import ttk

# Renkler
BG = "#12091A"         # Koyu mor-siyah arka plan
BG2 = "#1E112A"        # Biraz daha açık mor-siyah
CARD = "#2A183D"       # Kart arka planı (Koyu mor)
PURPLE = "#9D4EDD"     # Ana Vurgu (Parlak Mor)
PURPLE2 = "#7B2CBF"    # Vurgu 2 (Koyu Mor)
PURPLE_LIGHT = "#E0AAFF" # Açık Mor
WHITE = "#FFFFFF"
GRAY = "#A090A8"       # Gri morumsu
GREEN = "#4ADE80"
RED = "#F87171"

# Fontlar
FONT = ("Segoe UI", 11)
FONT_B = ("Segoe UI", 11, "bold")
FONT_H = ("Segoe UI", 22, "bold")
FONT_S = ("Segoe UI", 9)

def stil_ayarla(root):
    s = ttk.Style()
    # "clam" teması widgetları özelleştirmek için en iyisidir
    s.theme_use("clam")
    
    # Genel
    s.configure(".", background=BG, foreground=WHITE, font=FONT)
    s.configure("TFrame", background=BG)
    s.configure("Card.TFrame", background=CARD)
    
    # Etiketler (Labels)
    s.configure("TLabel", background=BG, foreground=WHITE, font=FONT)
    s.configure("Card.TLabel", background=CARD, foreground=WHITE)
    s.configure("Title.TLabel", background=BG, foreground=PURPLE, font=FONT_H)
    s.configure("CardTitle.TLabel", background=CARD, foreground=PURPLE, font=FONT_H)
    s.configure("Sub.TLabel", background=BG, foreground=GRAY, font=FONT_S)
    
    # Butonlar
    s.configure("Purple.TButton", background=PURPLE, foreground=WHITE, font=FONT_B, padding=(20,12), borderwidth=0)
    s.map("Purple.TButton", background=[("active", PURPLE2)])
    
    s.configure("Card.TButton", background=CARD, foreground=PURPLE_LIGHT, font=FONT, padding=(15,10), borderwidth=0)
    s.map("Card.TButton", background=[("active", "#3D255A")])
    
    s.configure("Side.TButton", background=BG2, foreground=PURPLE_LIGHT, font=FONT, padding=(15,12), anchor="w", borderwidth=0)
    s.map("Side.TButton", background=[("active", CARD)])
    
    # Girdi Alanları
    s.configure("TEntry", fieldbackground=BG2, foreground=WHITE, borderwidth=0, font=FONT, padding=8)
    
    # Açılır Kutular (Combobox)
    s.configure("TCombobox", fieldbackground=BG2, background=CARD, foreground=WHITE, borderwidth=0, arrowcolor=PURPLE_LIGHT, font=FONT, padding=5)
    s.map("TCombobox", fieldbackground=[("readonly", BG2)], selectbackground=[("readonly", PURPLE2)], selectforeground=[("readonly", WHITE)])
    root.option_add('*TCombobox*Listbox.background', BG2)
    root.option_add('*TCombobox*Listbox.foreground', WHITE)
    root.option_add('*TCombobox*Listbox.selectBackground', PURPLE)
    root.option_add('*TCombobox*Listbox.selectForeground', WHITE)
    root.option_add('*TCombobox*Listbox.font', FONT)
    
    # Kaydırma Çubuğu (Scrollbar)
    s.configure("Vertical.TScrollbar", background=CARD, troughcolor=BG, bordercolor=BG, arrowcolor=PURPLE_LIGHT, relief="flat", gripcount=0)
    s.map("Vertical.TScrollbar", background=[("active", PURPLE2)])
    s.configure("Horizontal.TScrollbar", background=CARD, troughcolor=BG, bordercolor=BG, arrowcolor=PURPLE_LIGHT, relief="flat", gripcount=0)
    s.map("Horizontal.TScrollbar", background=[("active", PURPLE2)])
    
    # Tablo (Treeview)
    s.configure("Treeview", background=BG2, foreground=WHITE, fieldbackground=BG2, borderwidth=0, font=FONT_S, rowheight=30)
    s.configure("Treeview.Heading", background=CARD, foreground=PURPLE, font=FONT_B, borderwidth=0)
    s.map("Treeview", background=[("selected", PURPLE2)])
    
    root.configure(bg=BG)

def temizle(frame):
    for w in frame.winfo_children():
        w.destroy()

def baslik_yaz(parent, metin, ikon="", is_card=False):
    style_frame = "Card.TFrame" if is_card else "TFrame"
    style_label = "CardTitle.TLabel" if is_card else "Title.TLabel"
    f = ttk.Frame(parent, style=style_frame)
    f.pack(fill="x", pady=(0,15))
    ttk.Label(f, text=f"{ikon}  {metin}", style=style_label).pack(anchor="w")
    tk.Frame(f, bg=PURPLE, height=2).pack(fill="x", pady=(8,0))
    return f

def form_alani(parent, etiket, gizli=False):
    ttk.Label(parent, text=etiket, style="Card.TLabel", font=("Segoe UI", 10)).pack(anchor="w", pady=(10,5))
    e = ttk.Entry(parent, show="●" if gizli else "", font=("Segoe UI", 12), width=28)
    e.pack(fill="x", pady=(0,15), ipady=6)
    return e

def tablo_olustur(parent, kolonlar, basliklar):
    f = ttk.Frame(parent)
    f.pack(fill="both", expand=True, pady=10)
    sb = ttk.Scrollbar(f)
    sb.pack(side="right", fill="y")
    t = ttk.Treeview(f, columns=kolonlar, show="headings", yscrollcommand=sb.set)
    for k, b in zip(kolonlar, basliklar):
        t.heading(k, text=b)
        t.column(k, width=100, anchor="center")
    t.pack(fill="both", expand=True)
    sb.config(command=t.yview)
    return t

def mesaj_goster(parent, mesaj, basari=True):
    renk = GREEN if basari else RED
    lbl = tk.Label(parent, text=mesaj, fg=renk, bg=BG, font=FONT)
    lbl.pack(pady=5)
    parent.after(3000, lbl.destroy)
