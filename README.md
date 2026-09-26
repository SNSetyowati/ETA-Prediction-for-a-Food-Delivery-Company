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
├── outputs/            # Hasil prediksi ETA & risiko untuk pesanan aktif
│   └── notifications/  # Draf email eskalasi & log pesanan lainnya
├── tests/              # Unit test (pytest)
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

## ⚡ Prediksi ETA & Risiko untuk Pesanan Aktif

Script `src/predict_eta.py` belajar dari data historis (`Capstone_Team1_CleanedData_v1_Zamato_Delivery_Operation.xlsx`, sheet *Zamato Delivery Filtering*) lalu memberi skor pada setiap pesanan di `active_deliveries_ZC.xlsx`.

**Output:** `outputs/active_deliveries_ZC_predicted.xlsx`

| Sheet | Isi |
|---|---|
| `Summary` | Ringkasan jumlah pesanan per kategori risiko, label kondisi, dan performa model |
| `Active_Deliveries` | Seluruh 50 pesanan + `Predicted_ETA_min`, `Risk_Score`, `Risk_Category`, label cuaca/lalu lintas/festival |
| `High_Critical` | Pesanan berisiko **High** dan **Critical** (perlu perhatian) |
| `Low_Medium` | Pesanan lainnya |
| `Backtest` | Perbandingan ETA prediksi vs. waktu aktual (`Ground_Truth`) |
| `Risk_Rules` | Tabel poin risiko & ambang kategori (dapat diubah, rumus otomatis menghitung ulang) |

Salinan CSV (`outputs/*.csv`) disediakan untuk kebutuhan dashboard.

**Predicted ETA** – model LightGBM dengan fitur: jarak (haversine), waktu tunggu pickup, jam pemesanan, cuaca, lalu lintas, festival, kota, jenis pesanan & kendaraan, kondisi kendaraan, multiple deliveries, serta usia & rating kurir. Pesanan historis yang sama dengan batch aktif dikeluarkan dari data latih agar backtest jujur.

**Risk Score** – mengikuti aturan skor risiko historis (cocok 100% pada 40.088 baris):

| Faktor | Poin |
|---|---|
| Cuaca | Sunny 0 · Windy 10 · Cloudy/Fog/Sandstorms/Stormy 20 |
| Lalu lintas | Low 0 · Medium 10 · High 20 · Jam 30 |
| Festival / event | Yes 30 |
| Multiple deliveries | 10 per pesanan tambahan |

Skor dibatasi maksimal 100. **Kategori:** Low (0–29) · Medium (30–49) · High (50–69) · Critical (≥70). Ambang ini diambil dari data historis: skor ≥70 → 57–95% pesanan memakan waktu >40 menit.

**Label:** Cuaca (Clear / Moderate / Adverse), Lalu lintas (Smooth / Moderate / Heavy / Severe), Festival (Normal Day / Festival / Event).

```bash
# Letakkan kedua file Excel di data/raw/, lalu:
python src/predict_eta.py
```

## 📧 Notifikasi Eskalasi

Script `src/notify.py` membaca `outputs/active_deliveries_ZC_predicted.csv`. Untuk setiap pesanan **High / Critical** dibuat tiga email:

| Penerima | Isi |
|---|---|
| Customer Service Lead | Alert risiko: skor, penyebab (cuaca, lalu lintas, festival), ETA, data driver, saran tindakan |
| Pelanggan | Pemberitahuan keterlambatan dan perkiraan jam tiba baru (tanpa detail risiko internal) |
| Driver | Alert risiko + rekomendasi rute: arah tujuan, link Google Maps, dan saran berdasarkan lalu lintas, cuaca, festival, dan jumlah pesanan |

Pesanan lainnya (Low / Medium) dicatat di `outputs/notifications/non_escalated_orders.log.csv`.

```bash
python src/notify.py          # dry run: simpan draf .eml di outputs/notifications/outbox/
python src/notify.py --send   # kirim via SMTP
```

Mode `--send` memerlukan `SMTP_HOST` (opsional `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`), `CS_LEAD_EMAIL`, dan alamat pelanggan/driver di `data/raw/contacts.csv` (kolom `Order_ID, customer_email, driver_email`). Alamat yang tidak tersedia memakai placeholder `@example.com` dan tidak akan dikirim. Status setiap email tercatat di `outputs/notifications/escalation_dispatch_log.csv`.

```bash
python -m pytest tests   # jalankan unit test
```

## 🏆 Hasil

| Model | MAE (menit) | RMSE (menit) | R² |
|---|---|---|---|
| Baseline (rata-rata) | 7,66 | – | – |
| LightGBM (hold-out 20%) | 3,05 | 3,80 | 0,838 |
| LightGBM (backtest 50 pesanan aktif) | 3,28 | 3,76 | – |

Batch aktif ZC: 14 High, 22 Medium, 14 Low, 0 Critical.

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
