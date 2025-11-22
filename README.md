# Dashboard Sales Analytics

Aplikasi dashboard sales analytics menggunakan Streamlit dengan visualisasi interaktif.

## 📁 Struktur Project

```
TugasABD/
├── app.py                 # Aplikasi utama (versi sederhana)
├── data/                  # Folder data CSV
│   ├── customers.csv
│   ├── products.csv
│   └── order_details.csv
├── requirements.txt       # Dependencies
└── Jet/                   # Versi aplikasi dengan visualisasi advanced
    ├── app.py
    ├── data/
    └── requirements.txt
```

## 🚀 Deploy ke Streamlit Cloud

### 1. Push ke GitHub
```bash
git add .
git commit -m "Deploy to Streamlit"
git push origin main
```

### 2. Deploy di Streamlit Cloud
1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Sign in dengan GitHub
3. Klik "New app"
4. Pilih:
   - Repository: `PutuNgurahSemara/TugasABD`
   - Branch: `main`
   - Main file: `app.py` atau `Jet/app.py`
5. Klik "Deploy"!

## 💻 Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run aplikasi
streamlit run app.py

# Atau versi Jet
cd Jet
streamlit run app.py
```

## 📊 Features

### Versi Standard (app.py)
- ✅ Customer management dengan filter usia
- ✅ Product analytics dengan bar chart
- ✅ Order tracking dan trends
- ✅ Export data ke CSV

### Versi Jets (Jet/app.py)
- ✅ Interactive Plotly visualizations
- ✅ Advanced analytics dashboard
- ✅ Time series analysis
- ✅ Heatmaps dan scatter plots
- ✅ Customer segmentation
- ✅ Product performance metrics

## 📦 Data

Data disimpan dalam format CSV di folder `data/`:
- `customers.csv`: Data pelanggan (100 records)
- `products.csv`: Data produk (50 records)
- `order_details.csv`: Detail transaksi (400+ records)

## 🔧 Tech Stack

- **Streamlit**: Web framework
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations (Jet version)
- **Matplotlib**: Static charts (Standard version)
