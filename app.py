import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Matematik Gelişim Takip", layout="wide")
st.title("📈 Matematik Gelişim Takip Sistemi")

# --- VERİ TABANI YÖNETİMİ ---
dosya_adi = "matematik_gelisim_verisi.csv"

def veri_yukle():
    try:
        # Okul numarasını metin olarak al, Tarihleri otomatik tanı
        df = pd.read_csv(dosya_adi, dtype={'Okul_No': str})
        # Kritik Düzeltme: Tarih sütununu datetime formatına çevir
        df["Tarih"] = pd.to_datetime(df["Tarih"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Tarih", "Okul_No", "Ogrenci_Adi", 
            "Kazanim_D", "Kazanim_Y", "Kazanim_B", 
            "Beceri_D", "Beceri_Y", "Beceri_B"
        ])

def veri_kaydet(df):
    df.to_csv(dosya_adi, index=False)

df = veri_yukle()

# --- SOL MENÜ: ÖĞRETMEN GİRİŞİ ---
st.sidebar.header("🔐 Öğretmen Paneli")
sifre = st.sidebar.text_input("Öğretmen Şifresi", type="password")
ogretmen_modu = False

if sifre == "1234":
    ogretmen_modu = True
    st.sidebar.success("Yönetici Girişi Yapıldı")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Sınıf Özeti")
    st.sidebar.write(f"Toplam Kayıt: {len(df)}")
    if not df.empty:
        st.sidebar.write(f"Farklı Öğrenci Sayısı: {df['Okul_No'].nunique()}")

# --- BÖLÜM 1: ÖĞRENCİ VERİ GİRİŞİ ---
st.subheader("📝 Günlük Veri Girişi")

with st.form("veri_giris_formu"):
    c1, c2, c3 = st.columns(3)
    okul_no = c1.text_input("Okul Numarası (Zorunlu)", max_chars=5) 
    ogrenci_adi = c2.text_input("Adın Soyadın").upper()
    tarih = c3.date_input("Tarih", date.today())
    
    st.info("Lütfen aşağıdaki sonuçları doğru giriniz.")
    
    # Kazanım Soruları
    st.markdown("**1. Kazanım Soruları**")
    k1, k2, k3 = st.columns(3)
    kd = k1.number_input("Kazanım DOĞRU", min_value=0)
    ky = k2.number_input("Kazanım YANLIŞ", min_value=0)
    kb = k3.number_input("Kazanım BOŞ", min_value=0)
    
    # Beceri Soruları
    st.markdown("**2. Beceri Temelli Sorular**")
    b1, b2, b3 = st.columns(3)
    bd = b1.number_input("Beceri DOĞRU", min_value=0)
    by = b2.number_input("Beceri YANLIŞ", min_value=0)
    bb = b3.number_input("Beceri BOŞ", min_value=0)
    
    kaydet = st.form_submit_button("Kaydet ve Gelişimimi Göster")

    if kaydet:
        if not okul_no or not ogrenci_adi:
            st.error("Lütfen Okul Numarası ve İsim alanlarını doldurun!")
        else:
            # Yeni kaydı oluştururken tarihi de datetime formatına çeviriyoruz
            yeni_kayit = {
                "Tarih": [pd.to_datetime(tarih)],
                "Okul_No": [okul_no],
                "Ogrenci_Adi": [ogrenci_adi],
                "Kazanim_D": [kd], "Kazanim_Y": [ky], "Kazanim_B": [kb],
                "Beceri_D": [bd], "Beceri_Y": [by], "Beceri_B": [bb]
            }
            yeni_df = pd.concat([df, pd.DataFrame(yeni_kayit)], ignore_index=True)
            veri_kaydet(yeni_df)
            df = yeni_df 
            st.success(f"{tarih} tarihli verilerin
