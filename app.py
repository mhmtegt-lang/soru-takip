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
        # Okul numarasını metin (string) olarak okuyalım ki virgül sorunu olmasın
        return pd.read_csv(dosya_adi, dtype={'Okul_No': str})
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
    
    # Öğretmen için genel analiz
    st.sidebar.markdown("---")
    st.sidebar.subheader("Sınıf Özeti")
    st.sidebar.write(f"Toplam Kayıt: {len(df)}")
    st.sidebar.write(f"Farklı Öğrenci Sayısı: {df['Okul_No'].nunique()}")

# --- BÖLÜM 1: ÖĞRENCİ VERİ GİRİŞİ ---
st.subheader("📝 Günlük Veri Girişi")

with st.form("veri_giris_formu"):
    c1, c2, c3 = st.columns(3)
    # Okul numarasını string alıyoruz (örn: 101, 102)
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
            yeni_kayit = {
                "Tarih": [tarih],
                "Okul_No": [okul_no],
                "Ogrenci_Adi": [ogrenci_adi],
                "Kazanim_D": [kd], "Kazanim_Y": [ky], "Kazanim_B": [kb],
                "Beceri_D": [bd], "Beceri_Y": [by], "Beceri_B": [bb]
            }
            yeni_df = pd.concat([df, pd.DataFrame(yeni_kayit)], ignore_index=True)
            veri_kaydet(yeni_df)
            df = yeni_df # Güncel veriyi hafızaya al
            st.success(f"{tarih} tarihli verilerin başarıyla kaydedildi!")

# --- BÖLÜM 2: ÖĞRENCİ GELİŞİM GRAFİKLERİ ---
# Okul numarası girildiyse hemen geçmişini dökelim
if okul_no:
    # Sadece o numaraya ait verileri çek
    ogr_gecmis = df[df["Okul_No"] == okul_no].sort_values("Tarih")
    
    if not ogr_gecmis.empty:
        st.markdown("---")
        st.header(f"📅 {ogrenci_adi} - Gelişim Tablosu")
        
        # Grafik için veriyi düzenle: Toplam Doğruyu Hesapla
        ogr_gecmis["Toplam Doğru"] = ogr_gecmis["Kazanim_D"] + ogr_gecmis["Beceri_D"]
        ogr_gecmis["Toplam Yanlış"] = ogr_gecmis["Kazanim_Y"] + ogr_gecmis["Beceri_Y"]

        # Çizgi Grafik (Line Chart) - Tarihsel Gelişim
        fig = px.line(ogr_gecmis, x="Tarih", y=["Toplam Doğru", "Toplam Yanlış"], 
                      markers=True, title="Gün Gün Doğru/Yanlış Değişimi")
        st.plotly_chart(fig, use_container_width=True)
        
        # Detaylı Sütun Grafik (Bar Chart)
        st.write("### Soru Tipine Göre Detaylı Gelişim")
        fig_bar = px.bar(ogr_gecmis, x="Tarih", y=["Kazanim_D", "Beceri_D"], 
                         title="Kazanım vs Beceri Doğru Sayıları",
                         labels={"value": "Soru Sayısı", "variable": "Soru Tipi"},
                         barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)

# --- BÖLÜM 3: ÖĞRETMEN LİSTESİ ---
if ogretmen_modu:
    st.markdown("---")
    st.header("📋 Tüm Sınıf Dökümü")
    st.dataframe(df)
    
    csv_indir = df.to_csv(index=False).encode('utf-8')
    st.download_button("Excel/CSV Olarak İndir", csv_indir, "sinif_takip.csv", "text/csv")
