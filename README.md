# E-Commerce Dashboard dengan Streamlit

**E-Commerce Dashboard** adalah aplikasi interaktif berbasis **Streamlit** yang menyajikan berbagai analisis dari dataset e-commerce. Dashboard ini membantu dalam memahami pola transaksi, pembayaran, dan pengiriman.

## Fitur Utama

- **Pola Pembayaran** → Menampilkan metode pembayaran yang paling sering digunakan.
- **Waktu Pengiriman** → Menghitung dan memvisualisasikan rata rata distribusi waktu pengiriman.
- **Jumlah Pesanan per Hari** → Analisis jumlah pesanan berdasarkan hari dalam seminggu.
- **Rata-rata Nilai Transaksi** → Menampilkan rata-rata nilai transaksi berdasarkan metode pembayaran.

## Dataset yang Digunakan

- `orders_dataset.csv` → Data pesanan pelanggan.
- `order_payments_dataset.csv` → Data pembayaran pelanggan.
- `order_items_dataset.csv` → Detail item dalam pesanan.
- `products_dataset.csv` → Informasi produk.

## Cara Menjalankan

### **Persiapan Lingkungan**

Pastikan Anda sudah menginstall semua dependensi dengan perintah berikut:

```sh
pip install -r requirements.txt
```

### **Menjalankan Aplikasi**

Masuk kedalam folder dashboard, lalu jalankan perintah berikut:

```sh
streamlit run dashboard.py
```

### **Mengakses Dashboard**

Setelah dijalankan, buka browser dan akses:

```
http://localhost:8501
```
