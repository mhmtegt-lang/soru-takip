import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Matematik Takip Sistemi", layout="wide")

# Başlık
st.title("🧮 Matematik Soru Takip Sistemi")

# --- VERİ TABANI (Geçici CSV) ---
# Not: Streamlit Cloud yeniden başlatıldığında CSV sıfırlanabilir.
# Kalıcı olması için Google Sheets bağlamak gerekir (İleride yapabiliriz).
dosya_adi = "matematik_verisi.csv"

def veri_yukle():
    try:
        return pd.read_csv(dosya_adi)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Tarih", "Ogrenci_Adi", 
            "Kazanim_D", "Kazanim_Y", "Kazanim_B", 
            "Beceri_D", "Beceri_Y", "Beceri_B"
        ])

def veri_kaydet(df):
    df.to_csv(dosya_adi, index=False)

df = veri_yukle()

# --- SOL MENÜ (ÖĞRETMEN GİRİŞİ) ---
st.sidebar.header("🔐 Öğretmen Paneli")
sifre = st.sidebar.text_input("Şifre", type="password")
ogretmen_modu = False

if sifre == "1234":  # Şifreyi buradan değiştirebilirsiniz
    ogretmen_modu = True
    st.sidebar.success("Giriş Başarılı!")
elif sifre:
    st.sidebar.error("Hatalı Şifre")

# --- BÖLÜM 1: ÖĞRENCİ VERİ GİRİŞİ ---
st.subheader("📝 Günlük Soru Girişi")

with st.form("veri_giris"):
    col_ad, col_tarih = st.columns(2)
    ogrenci_adi = col_ad.text_input("Adın Soyadın").upper()
    tarih = col_tarih.date_input("Tarih", date.today())
    
    st.markdown("---")
    
    # Kazanım Soruları
    st.write("### 1. Kazanım Soruları")
    k1, k2, k3 = st.columns(3)
    kazanim_d = k1.number_input("Kazanım DOĞRU", min_value=0, value=0)
    kazanim_y = k2.number_input("Kazanım YANLIŞ", min_value=0, value=0)
    kazanim_b = k3.number_input("Kazanım BOŞ", min_value=0, value=0)
    
    # Beceri Temelli Sorular
    st.write("### 2. Beceri Temelli (Yeni Nesil) Sorular")
    b1, b2, b3 = st.columns(3)
    beceri_d = b1.number_input("Beceri DOĞRU", min_value=0, value=0)
    beceri_y = b2.number_input("Beceri YANLIŞ", min_value=0, value=0)
    beceri_b = b3.number_input("Beceri BOŞ", min_value=0, value=0)
    
    kaydet_btn = st.form_submit_button("Sonuçları Kaydet ve Grafiği Gör")

    if kaydet_btn and ogrenci_adi:
        yeni_veri = {
            "Tarih": [tarih],
            "Ogrenci_Adi": [ogrenci_adi],
            "Kazanim_D": [kazanim_d], "Kazanim_Y": [kazanim_y], "Kazanim_B": [kazanim_b],
            "Beceri_D": [beceri_d], "Beceri_Y": [beceri_y], "Beceri_B": [beceri_b]
        }
        yeni_df = pd.concat([df, pd.DataFrame(yeni_veri)], ignore_index=True)
        veri_kaydet(yeni_df)
        df = yeni_df # Listeyi güncelle
        st.success(f"Tebrikler {ogrenci_adi}, verilerin kaydedildi!")

# --- BÖLÜM 2: GRAFİKLER ---

# Eğer öğrenci ismini girdiyse veya kaydettiyse, ona özel grafiği göster
if ogrenci_adi:
    ogr_df = df[df["Ogrenci_Adi"] == ogrenci_adi]
    
    if not ogr_df.empty:
        st.markdown("---")
        st.subheader(f"📊 {ogrenci_adi} İçin Performans Analizi")
        
        # Toplam Veriler
        toplam_kazanim = ogr_df["Kazanim_D"].sum() + ogr_df["Kazanim_Y"].sum() + ogr_df["Kazanim_B"].sum()
        toplam_beceri = ogr_df["Beceri_D"].sum() + ogr_df["Beceri_Y"].sum() + ogr_df["Beceri_B"].sum()
        
        # Grafik Alanı
        g1, g2 = st.columns(2)
        
        # Grafik 1: Doğru/Yanlış Dağılımı (Pasta Grafik)
        toplam_dogru = ogr_df["Kazanim_D"].sum() + ogr_df["Beceri_D"].sum()
        toplam_yanlis = ogr_df["Kazanim_Y"].sum() + ogr_df["Beceri_Y"].sum()
        toplam_bos = ogr_df["Kazanim_B"].sum() + ogr_df["Beceri_B"].sum()
        
        fig_pie = px.pie(
            names=["Doğru", "Yanlış", "Boş"], 
            values=[toplam_dogru, toplam_yanlis, toplam_bos],
            title="Genel Başarı Oranı",
            color_discrete_sequence=["green", "red", "gray"]
        )
        g1.plotly_chart(fig_pie, use_container_width=True)
        
        # Grafik 2: Kazanım vs Beceri (Sütun Grafik)
        fig_bar = go.Figure(data=[
            go.Bar(name='Doğru', x=['Kazanım', 'Beceri'], y=[ogr_df["Kazanim_D"].sum(), ogr_df["Beceri_D"].sum()], marker_color='green'),
            go.Bar(name='Yanlış', x=['Kazanım', 'Beceri'], y=[ogr_df["Kazanim_Y"].sum(), ogr_df["Beceri_Y"].sum()], marker_color='red')
        ])
        fig_bar.update_layout(barmode='group', title="Soru Tipine Göre Analiz")
        g2.plotly_chart(fig_bar, use_container_width=True)

# --- BÖLÜM 3: ÖĞRETMEN ÖZEL ALANI ---
if ogretmen_modu:
    st.markdown("---")
    st.header("📋 Tüm Sınıf Listesi (Sadece Öğretmen Görür)")
    
    # Tabloyu düzenle
    gosterim_df = df.copy()
    gosterim_df["Toplam Soru"] = (
        gosterim_df["Kazanim_D"] + gosterim_df["Kazanim_Y"] + gosterim_df["Kazanim_B"] +
        gosterim_df["Beceri_D"] + gosterim_df["Beceri_Y"] + gosterim_df["Beceri_B"]
    )
    
    st.dataframe(gosterim_df)
    
    # İndirme Butonu
    csv = gosterim_df.to_csv(index=False).encode('utf-8')
    st.download_button("Listeyi İndir (Excel/CSV)", csv, "sinif_listesi.csv", "text/csv")

elif not ogretmen_modu and not ogrenci_adi:
    st.info("Kendi grafiğini görmek için yukarıya ismini yazmalısın. Tüm listeyi görmek için sol menüden öğretmen girişi yapmalısın.")
