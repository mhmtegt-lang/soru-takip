import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Eğitim Takip Sistemi", layout="wide")
st.title("🎓 Dijital Eğitim Takip Sistemi")

# --- SABİT VERİLER (MEB MÜFREDATI) ---
MEB_KONULARI = {
    "5. Sınıf": ["Doğal Sayılar", "Doğal Sayılarla İşlemler", "Kesirler", "Ondalık Gösterim", "Yüzdeler", "Temel Geometrik Kavramlar", "Üçgenler ve Dörtgenler", "Veri Toplama ve Değerlendirme", "Uzunluk ve Zaman Ölçme", "Alan Ölçme", "Geometrik Cisimler"],
    "6. Sınıf": ["Doğal Sayılarla İşlemler", "Çarpanlar ve Katlar", "Kümeler", "Tam Sayılar", "Kesirlerle İşlemler", "Ondalık Gösterim", "Oran", "Cebirsel İfadeler", "Veri Analizi", "Açılar", "Alan Ölçme", "Çember", "Geometrik Cisimler", "Sıvı Ölçme"],
    "7. Sınıf": ["Tam Sayılarla İşlemler", "Rasyonel Sayılar", "Rasyonel Sayılarla İşlemler", "Cebirsel İfadeler", "Eşitlik ve Denklem", "Oran ve Orantı", "Yüzdeler", "Doğrular ve Açılar", "Çokgenler", "Çember ve Daire", "Veri Analizi", "Cisimlerin Görünümleri"],
    "8. Sınıf (LGS)": ["Çarpanlar ve Katlar", "Üslü İfadeler", "Kareköklü İfadeler", "Veri Analizi", "Basit Olayların Olma Olasılığı", "Cebirsel İfadeler ve Özdeşlikler", "Doğrusal Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik ve Benzerlik", "Dönüşüm Geometrisi", "Geometrik Cisimler"]
}

# --- VERİ TABANI YÖNETİMİ ---
dosya_adi = "gelismis_takip_verisi.csv"
duyuru_dosyasi = "duyuru.txt"

def veri_yukle():
    try:
        df = pd.read_csv(dosya_adi, dtype={'Okul_No': str})
        df["Tarih"] = pd.to_datetime(df["Tarih"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Tarih", "Okul_No", "Ogrenci_Adi", "Sinif", "Konu",
            "Kazanim_D", "Kazanim_Y", "Kazanim_B", 
            "Beceri_D", "Beceri_Y", "Beceri_B"
        ])

def veri_kaydet(df):
    df.to_csv(dosya_adi, index=False)

def duyuru_oku():
    try:
        with open(duyuru_dosyasi, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Henüz bir duyuru yok."

def duyuru_yaz(mesaj):
    with open(duyuru_dosyasi, "w", encoding="utf-8") as f:
        f.write(mesaj)

df = veri_yukle()

# --- SOL MENÜ: ÖĞRETMEN GİRİŞİ ---
st.sidebar.header("🔐 Öğretmen Paneli")
sifre = st.sidebar.text_input("Öğretmen Şifresi", type="password")
ogretmen_modu = False

if sifre == "1234":
    ogretmen_modu = True
    st.sidebar.success("Öğretmen Girişi Başarılı")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📢 Duyuru Panosu")
    yeni_duyuru = st.sidebar.text_area("Öğrencilere Mesajınız:", value=duyuru_oku())
    if st.sidebar.button("Duyuruyu Güncelle"):
        duyuru_yaz(yeni_duyuru)
        st.sidebar.success("Duyuru güncellendi!")

# --- ANA EKRAN: DUYURU ALANI ---
aktif_duyuru = duyuru_oku()
if aktif_duyuru and aktif_duyuru != "Henüz bir duyuru yok.":
    st.info(f"📢 **ÖĞRETMEN DUYURUSU:** {aktif_duyuru}")

# --- BÖLÜM 1: ÖĞRENCİ VERİ GİRİŞİ ---
st.subheader("📝 Veri Girişi")

c1, c2, c3 = st.columns(3)
okul_no = c1.text_input("Okul Numarası (Zorunlu)", max_chars=5) 
ogrenci_adi = c2.text_input("Adın Soyadın").upper()
tarih = c3.date_input("Tarih", date.today())

c4, c5 = st.columns(2)
secilen_sinif = c4.selectbox("Sınıfını Seç", list(MEB_KONULARI.keys()))
secilen_konu = c5.selectbox("Bugün Hangi Konuyu Çalıştın?", MEB_KONULARI[secilen_sinif])

st.markdown("---")
st.write("Performans Sonuçları:")

col_kazanim, col_beceri = st.columns(2)

with col_kazanim:
    st.markdown("**1. Kazanım (Temel) Sorular**")
    kd = st.number_input("Doğru", min_value=0, key="kd")
    ky = st.number_input("Yanlış", min_value=0, key="ky")
    kb = st.number_input("Boş", min_value=0, key="kb")

with col_beceri:
    st.markdown("**2. Beceri (Yeni Nesil) Sorular**")
    bd = st.number_input("Doğru", min_value=0, key="bd")
    by = st
