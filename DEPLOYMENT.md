# 🚀 Panduan Deploy ke Streamlit Cloud

## ✅ Persiapan Selesai!

Data sudah di-export ke CSV dan aplikasi sudah diupdate untuk membaca dari file CSV.

## 📝 Langkah Deploy

### 1. **Push ke GitHub**

```powershell
# Pastikan di folder TugasABD
cd C:\TugasABD

# Add semua file
git add .

# Commit dengan pesan
git commit -m "Ready for Streamlit Cloud deployment"

# Push ke GitHub
git push origin main
```

### 2. **Deploy di Streamlit Cloud**

1. **Buka browser** dan kunjungi: [share.streamlit.io](https://share.streamlit.io)

2. **Sign In** menggunakan akun GitHub Anda

3. **Klik tombol "New app"**

4. **Isi form deployment:**
   - **Repository:** `PutuNgurahSemara/TugasABD`
   - **Branch:** `main`
   - **Main file path:** 
     - Untuk versi standard: `app.py`
     - Untuk versi Jets: `Jet/app.py`

5. **Klik "Deploy!"**

   Streamlit akan:
   - Install dependencies dari `requirements.txt`
   - Load data dari folder `data/`
   - Deploy aplikasi Anda secara otomatis

6. **Tunggu beberapa menit** sampai deployment selesai

7. **Aplikasi siap!** Anda akan mendapat URL seperti:
   - `https://putungurahsemara-tugasabd-app-xxxxx.streamlit.app`

## 🔍 File yang Akan Di-Upload

✅ **File yang dibutuhkan:**
- `app.py` atau `Jet/app.py` (aplikasi utama)
- `requirements.txt` (dependencies)
- `data/customers.csv`
- `data/products.csv`
- `data/order_details.csv`
- `README.md` (dokumentasi)

❌ **File yang TIDAK diupload** (sudah ada di .gitignore):
- `config.py` (berisi password database)
- `__pycache__/`
- `.vscode/`
- File database lokal

## 📊 Pilihan Aplikasi

### Opsi 1: Versi Standard (`app.py`)
- Lebih ringan dan cepat load
- Chart bawaan Streamlit
- Cocok untuk dashboard sederhana

### Opsi 2: Versi Jets (`Jet/app.py`)
- Visualisasi interaktif dengan Plotly
- Dashboard lebih komprehensif
- Multiple tabs dan advanced analytics

## 🎯 Tips Deploy

1. **Jika deployment gagal**, cek di logs:
   - Error biasanya terkait dependencies
   - Pastikan semua file CSV ada di folder `data/`

2. **Update aplikasi:**
   ```powershell
   git add .
   git commit -m "Update aplikasi"
   git push origin main
   ```
   Streamlit akan auto-redeploy!

3. **Monitor usage:**
   - Free tier: unlimited public apps
   - Private apps: perlu upgrade

## 🔗 Setelah Deploy

Bagikan URL aplikasi Anda:
- Link akan berbentuk: `https://[username]-[repo]-[file]-xxxxx.streamlit.app`
- Bisa di-custom di settings Streamlit Cloud
- Share ke siapa saja!

## ❓ Troubleshooting

**Error: Module not found**
- Pastikan library ada di `requirements.txt`
- Redeploy dengan force restart

**Error: File not found**
- Cek path file CSV relatif ke `app.py`
- Pastikan folder `data/` ter-push ke GitHub

**App lambat**
- Gunakan `@st.cache_data` untuk caching
- Sudah diimplementasi di kedua versi

## 📞 Support

Jika ada masalah:
1. Cek [Streamlit Community Forum](https://discuss.streamlit.io)
2. Lihat [Streamlit Documentation](https://docs.streamlit.io)
3. Check logs di Streamlit Cloud dashboard
