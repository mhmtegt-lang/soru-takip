import streamlit as st
import pandas as pd
import plotly.express as px
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

# Form yapısını kaldırdık, artık anlık güncellenecek
c1, c2, c3 = st.columns(3)
okul_no = c1.text_input("Okul Numarası (Zorunlu)", max_chars=5) 
ogrenci_adi = c2.text_input("Adın Soyadın").upper()
tarih = c3.date_input("Tarih", date.today())

# Sınıf ve Konu Seçimi (Artık burası canlı çalışır)
c4, c5 = st.columns(2)
secilen_sinif = c4.selectbox("Sınıfını Seç", list(MEB_KONULARI.keys()))
# Sınıf değişince buradaki liste otomatik yenilenir
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
    by = st.number_input("Yanlış", min_value=0, key="by")
    bb = st.number_input("Boş", min_value=0, key="bb")

st.markdown("---")
kaydet = st.button("Kaydet ve Analiz Et")

if kaydet:
    if not okul_no or not ogrenci_adi:
        st.error("Lütfen Okul No ve İsim giriniz!")
    else:
        yeni_kayit = {
            "Tarih": [pd.to_datetime(tarih)],
            "Okul_No": [okul_no],
            "Ogrenci_Adi": [ogrenci_adi],
            "Sinif": [secilen_sinif],
            "Konu": [secilen_konu],
            "Kazanim_D": [kd], "Kazanim_Y": [ky], "Kazanim_B": [kb],
            "Beceri_D": [bd], "Beceri_Y": [by], "Beceri_B": [bb]
        }
        yeni_df = pd.concat([df, pd.DataFrame(yeni_kayit)], ignore_index=True)
        veri_kaydet(yeni_df)
        df = yeni_df 
        st.success(f"Tebrikler {ogrenci_adi}! {secilen_konu} konusundaki çalışman kaydedildi.")

# --- BÖLÜM 2: ANALİZ VE KARNE ---
if okul_no:
    ogr_df = df[df["Okul_No"] == okul_no].copy()
    
    if not ogr_df.empty:
        st.markdown("---")
        st.subheader("🎯 Haftalık Hedef Durumu")
        
        # Son 7 günün verisini filtrele
        bir_hafta_once = pd.to_datetime(date.today() - timedelta(days=7))
        haftalik_df = ogr_df[ogr_df["Tarih"] >= bir_hafta_once]
        
        toplam_cozulen = (haftalik_df["Kazanim_D"] + haftalik_df["Kazanim_Y"] + haftalik_df["Kazanim_B"] +
                          haftalik_df["Beceri_D"] + haftalik_df["Beceri_Y"] + haftalik_df["Beceri_B"]).sum()
        
        HEDEF = 150
        ilerleme = min(toplam_cozulen / HEDEF, 1.0)
        
        st.progress(ilerleme)
        st.caption(f"Bu hafta toplam **{toplam_cozulen}** soru çözdün. Hedef: {HEDEF} soru. %{int(ilerleme*100)} tamamlandı!")
        
        if toplam_cozulen >= HEDEF:
            st.balloons()
            st.success("🏆 HARİKASIN! Haftalık hedefini tamamladın!")

        # Veli Karnesi ve Grafik
        st.markdown("---")
        c_grafik, c_karne = st.columns([2, 1])
        
        with c_grafik:
            st.subheader("📈 Gelişim Grafiği")
            ogr_df = ogr_df.sort_values("Tarih")
            ogr_df["Toplam Doğru"] = ogr_df["Kazanim_D"] + ogr_df["Beceri_D"]
            fig = px.line(ogr_df, x="Tarih", y="Toplam Doğru", title="Günlük Doğru Sayısı", markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with c_karne:
            st.subheader("👨‍👩‍👦 Veli Bilgilendirme")
            st.write("Aşağıdaki butona basarak velin için özet bir kart oluşturabilirsin.")
            
            if st.button("Veli Karnesi Oluştur"):
                toplam_d = ogr_df["Kazanim_D"].sum() + ogr_df["Beceri_D"].sum()
                toplam_y = ogr_df["Kazanim_Y"].sum() + ogr_df["Beceri_Y"].sum()
                genel_basari = int((toplam_d / (toplam_d + toplam_y + 1)) * 100)
                en_cok_cozulen = ogr_df["Konu"].mode()[0] if not ogr_df["Konu"].empty else "Yok"
                
                karne_metni = f"""
                📢 **SAYIN VELİMİZ,**
                
                Öğrenciniz **{ogrenci_adi}** için güncel durum raporu:
                
                ✅ **Toplam Doğru:** {toplam_d}
                📉 **Toplam Yanlış:** {toplam_y}
                📊 **Genel Başarı:** %{genel_basari}
                📚 **En Çok Çalışılan Konu:** {en_cok_cozulen}
                🎯 **Haftalık Hedef Durumu:** %{int(ilerleme*100)}
                
                *Bu rapor Dijital Eğitim Takip Sistemi tarafından oluşturulmuştur.*
                """
                st.info(karne_metni)

# --- BÖLÜM 3: ÖĞRETMEN LİSTESİ ---
if ogretmen_modu:
    st.markdown("---")
    st.header("📋 Tüm Sınıf Dökümü")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Listeyi İndir", csv, "sinif_listesi.csv", "text/csv")
