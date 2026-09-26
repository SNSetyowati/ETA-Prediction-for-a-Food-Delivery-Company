# 🛵 Prediksi Estimated Time of Arrival (ETA) untuk Perusahaan Food Delivery

Memprediksi waktu pengiriman makanan (ETA) menggunakan machine learning untuk meningkatkan pengalaman pelanggan, alokasi kurir, dan efisiensi operasional.

---

## 📌 Gambaran Proyek

Pengiriman yang cepat memang membuat pelanggan puas, tetapi yang tidak kalah penting adalah **estimasi waktu (ETA) yang akurat**. Jika aplikasi menjanjikan waktu tiba lebih cepat daripada kenyataannya (misalnya ETA 20 menit, tetapi pesanan baru tiba dalam 40 menit), pelanggan akan merasa kecewa karena ekspektasinya tidak terpenuhi. Sebaliknya, jika ETA yang ditampilkan jauh lebih lama daripada waktu sebenarnya, pelanggan bisa mengurungkan niat memesan sehingga konversi pesanan menurun. Proyek ini membangun model regresi untuk memprediksi berapa lama sebuah pesanan akan sampai, berdasarkan faktor pesanan, restoran, kurir, dan lingkungan.

## 🎯 Tujuan

- Mengeksplorasi dan memahami faktor-faktor utama yang memengaruhi waktu pengiriman.
- Membangun dan mengevaluasi model machine learning untuk memprediksi ETA (dalam menit).
- Menyajikan insight dan rekomendasi bisnis dalam bentuk **report**.
- Menampilkan hasil analisis melalui **dashboard** interaktif.

## 📊 Dataset

Dataset berisi data pesanan food delivery dengan fitur-fitur seperti:

| Kategori | Contoh Fitur |
|---|---|
| Kurir | usia, rating, jenis kendaraan, kondisi kendaraan |
| Lokasi | koordinat restoran & tujuan, jarak, tipe kota |
| Pesanan | jenis pesanan, tanggal pesanan, waktu pesan, waktu pickup |
| Lingkungan | kondisi cuaca, kepadatan lalu lintas, festival |
| Target | `time_taken (min)` |

> Simpan data mentah di `data/raw/` dan data hasil olahan di `data/processed/` (file data tidak disimpan di Git).

## 🗂️ Struktur Proyek

```
ETA-Prediction-for-a-Food-Delivery-Company/
├── data/
│   ├── raw/            # Dataset asli (tidak diubah)
│   └── processed/      # Data yang sudah dibersihkan & feature engineering
├── notebooks/          # Jupyter notebook (EDA, modeling, evaluasi)
├── src/                # Script Python (preprocessing, fitur, training)
├── models/             # Model yang sudah dilatih
├── report/             # Laporan akhir / presentasi (PDF, PPT, grafik)
├── dashboard/          # File dashboard (Tableau / Power BI / Looker Studio / Streamlit)
├── requirements.txt    # Daftar library Python
└── README.md
```

## 🔄 Alur Kerja

1. **Business Understanding** – mendefinisikan masalah dan metrik keberhasilan.
2. **Data Understanding & EDA** – distribusi data, korelasi, dan faktor utama waktu pengiriman.
3. **Data Preparation** – pembersihan data, penanganan missing value, outlier, dan encoding.
4. **Feature Engineering** – jarak haversine, jam pemesanan, hari dalam seminggu, waktu persiapan, dll.
5. **Modeling** – baseline (Linear Regression) vs. model berbasis tree (Random Forest, XGBoost, LightGBM).
6. **Evaluasi** – MAE, RMSE, dan R² pada data test.
7. **Report & Dashboard** – mengomunikasikan insight dan hasil model kepada stakeholder.

## 📈 Metrik Evaluasi

| Metrik | Deskripsi |
|---|---|
| **MAE** | Rata-rata selisih absolut dalam menit — mudah dipahami oleh tim bisnis |
| **RMSE** | Memberi penalti lebih besar pada error yang besar |
| **R²** | Proporsi variasi waktu pengiriman yang dapat dijelaskan oleh model |

## 🏆 Hasil

_Akan diperbarui setelah proses modeling._

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Linear Regression | – | – | – |
| Random Forest | – | – | – |
| XGBoost | – | – | – |

## 📑 Report

Analisis lengkap, insight, dan rekomendasi bisnis tersedia di folder [`report/`](report/).

## 📊 Dashboard

Dashboard interaktif tersedia di folder [`dashboard/`](dashboard/).

## 🚀 Cara Menjalankan

```bash
# Clone repository
git clone https://github.com/SNSetyowati/ETA-Prediction-for-a-Food-Delivery-Company.git
cd ETA-Prediction-for-a-Food-Delivery-Company

# Buat virtual environment dan install library
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Jalankan Jupyter
jupyter notebook
```

## 🛠️ Tools & Teknologi

Python · Pandas · NumPy · Scikit-learn · XGBoost · LightGBM · Matplotlib · Seaborn · Jupyter · Streamlit / Tableau

## 👤 Author

**SN Setyowati**
- GitHub: [@SNSetyowati](https://github.com/SNSetyowati)
