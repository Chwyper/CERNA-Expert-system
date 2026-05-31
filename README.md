# CERNA v2.0 — Sistem Pakar Diagnosa Kesehatan Mental

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Framework-black?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

CERNA adalah sebuah Sistem Pakar berbasis web (Rule-Based Expert System) yang dirancang untuk membantu melakukan _screening_ awal terhadap kondisi kesehatan mental. Aplikasi ini menggunakan pendekatan **Depth-First Search (DFS)** dikombinasikan dengan metode **Certainty Factor (CF)** untuk menghitung tingkat keyakinan diagnosis berdasarkan gejala yang dipilih oleh pengguna.

Diagnosis dan gejala yang digunakan dalam sistem ini diadaptasi dari standar SDKI (Standar Diagnosis Keperawatan Indonesia).

---

## 🌟 Fitur Utama

- **Asesmen Kesehatan Mental Terstruktur**: Pengguna dapat memilih kategori gejala dan menjawab serangkaian pertanyaan berbasis form (Rule-Based).
- **Algoritma DFS & Certainty Factor**: Sistem secara dinamis menelusuri rule dan menghitung bobot kemungkinan dari 12 diagnosis dan 75 gejala.
- **Admin Dashboard**: Panel khusus administrator untuk melakukan modifikasi pada Knowledge Base (menambah/menghapus/mengedit penyakit, gejala, dan nilai CF) secara interaktif langsung dari UI (tanpa harus menyentuh kode).
- **Modern & Responsive UI**: Dibangun dengan antarmuka yang ramah pengguna, berdesain _clean_, serta didukung oleh tipografi modern (Lora & Inter).

---

## 🛠️ Teknologi yang Digunakan

- **Backend**: Python, Flask
- **Frontend**: HTML5, Vanilla CSS, Jinja2 Templating (Modular menggunakan `base.html`)
- **Algoritma**: DFS (Depth-First Search) + Certainty Factor (CF)

---

## 📂 Struktur Direktori

```text
CERNA/
├── app.py                  # Entry point aplikasi & Core Routes (Flask)
├── dfs.py                  # Logika algoritma pencarian (DFS & Certainty Factor)
├── requirements.txt        # Daftar dependensi modul Python
├── templates/              # File Jinja2 HTML Templates
│   ├── base.html           # Master layout untuk halaman pengguna
│   ├── index.html          # Landing page
│   ├── pilih_metode.html   # Halaman pemilihan tipe asesmen
│   ├── asesmen_manual.html # Grid pemilihan kategori asesmen
│   ├── asesmen.html        # UI Kuesioner dan Hasil Asesmen
│   ├── admin_login.html    # Halaman login administrator
│   ├── admin_dashboard.html# Dashboard admin utama
│   └── admin_detail.html   # Halaman edit detail penyakit/gejala
└── _context/               # Direktori catatan pengembangan & dokumentasi prompt
```

---

## 🚀 Panduan Instalasi dan Menjalankan Aplikasi

Pastikan Python versi 3.x sudah terinstal di komputer Anda.

1. **Clone Repositori**
   ```bash
   git clone https://github.com/Chwyper/CERNA-Expert-system.git
   cd CERNA-Expert-system
   ```

2. **Buat dan Aktifkan Virtual Environment (Direkomendasikan)**
   ```bash
   # Di Windows:
   python -m venv .venv
   .venv\Scripts\activate
   
   # Di macOS/Linux:
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instal Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan Aplikasi**
   ```bash
   python app.py
   ```

5. **Akses via Browser**
   Buka `http://127.0.0.1:5000` di web browser pilihan Anda.

---

## ⚙️ Akses Administrator

Untuk mengakses Dashboard Admin dan mengedit _Knowledge Base_:
- Buka URL: `http://127.0.0.1:5000/admin`
- Password _Default_: **`admin123`** *(Dapat dikonfigurasi pada `app.py`)*

---

## ⚠️ Disclaimer (Peringatan Penting)

Aplikasi ini dikembangkan untuk tujuan edukasi dan _screening_ awal (Sistem Pakar). **CERNA tidak dimaksudkan untuk menggantikan diagnosis medis profesional.** Semua hasil asesmen harus dikonsultasikan lebih lanjut dengan psikolog, psikiater, atau tenaga profesional medis yang berwenang.

---

**Dikembangkan oleh:**  
ITENAS Bandung &middot; 2026
