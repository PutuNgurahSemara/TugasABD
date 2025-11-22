# Import library
import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config("Dashboard Sales", page_icon="📊", layout="wide")

# =====================================================
# LOAD DATA DARI CSV
# =====================================================
@st.cache_data
def load_data():
    """Load data dari CSV files"""
    try:
        # Coba load dari folder data
        df_customers = pd.read_csv('data/customers.csv')
        df_products = pd.read_csv('data/products.csv')
        df_order_details = pd.read_csv('data/order_details.csv')
        return df_customers, df_products, df_order_details
    except FileNotFoundError:
        st.error("⚠️ File CSV tidak ditemukan! Pastikan folder 'data' berisi file CSV.")
        st.stop()

# Load data
df_customers, df_products, df_order_details = load_data()

# =====================================================
# PREPROCESSING DATA
# =====================================================
# Hitung usia dari birthdate
df_customers['birthdate'] = pd.to_datetime(df_customers['birthdate'])
df_customers['Age'] = (datetime.now() - df_customers['birthdate']).dt.days // 365

# =====================================================
# FUNGSI: TAMPILAN PELANGGAN
# =====================================================
def tabelCustomers_dan_export():
    """Menampilkan tabel pelanggan dengan filter usia dan export CSV"""
    
    total_customers = df_customers.shape[0]

    # Metrik
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📦 Total Pelanggan", value=total_customers, delta="Semua Data")

    # Sidebar: Filter Rentang Usia
    st.sidebar.header("Filter Rentang Usia")
    min_age = int(df_customers['Age'].min())
    max_age = int(df_customers['Age'].max())
    age_range = st.sidebar.slider(
        "Pilih Rentang Usia",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age),
        key="customer_age_range"
    )

    # Terapkan filter usia
    filtered_df = df_customers[df_customers['Age'].between(*age_range)]

    # Tampilkan tabel pelanggan
    st.markdown("### 📋 Tabel Data Pelanggan")
    
    showdata = st.multiselect(
        "Pilih Kolom Pelanggan yang Ditampilkan",
        options=filtered_df.columns,
        default=["customer_id", "name", "email", "phone", "address", "birthdate", "Age"],
        key="customer_columns"
    )
    
    # Sorting dengan dropdown tunggal
    sort_options = []
    for col in filtered_df.columns:
        sort_options.append(f"{col} (ASC ↑)")
        sort_options.append(f"{col} (DESC ↓)")
    
    sort_selection = st.selectbox(
        "Urutkan berdasarkan",
        options=sort_options,
        index=sort_options.index("name (ASC ↑)") if "name (ASC ↑)" in sort_options else 0,
        key="customer_sort"
    )
    
    # Parse selection
    sort_by = sort_selection.rsplit(" (", 1)[0]
    ascending = "ASC" in sort_selection
    sorted_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
    
    st.dataframe(sorted_df[showdata], use_container_width=True)

    # Export CSV
    @st.cache_data
    def convert_df_to_csv(_df):
        return _df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df_to_csv(sorted_df[showdata])
    st.download_button(
        label="⬇️ Download Data Pelanggan sebagai CSV",
        data=csv,
        file_name='data_pelanggan.csv',
        mime='text/csv'
    )

# =====================================================
# FUNGSI: TAMPILAN ORDER
# =====================================================
def tabelOrders_dan_chart():
    """Menampilkan data order dengan grafik pembelian barang"""
    
    df_local = df_order_details.copy()
    if df_local.empty:
        st.info("Belum ada data order untuk ditampilkan.")
        return

    # Konversi tipe data
    df_local['order_date'] = pd.to_datetime(df_local['order_date'])
    df_local['quantity'] = pd.to_numeric(df_local['quantity'], errors='coerce').fillna(0).astype(int)
    df_local['subtotal'] = pd.to_numeric(df_local['subtotal'], errors='coerce')

    # Sidebar: Filter tanggal dan pencarian produk
    st.sidebar.header("Filter Order")
    min_date = df_local['order_date'].min().date()
    max_date = df_local['order_date'].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Rentang Tanggal Order",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="order_date_filter"
    )
    search_product = st.sidebar.text_input("Cari Nama Produk", value="", key="order_search_product")

    # Terapkan filter tanggal
    mask = (df_local['order_date'].dt.date >= start_date) & (df_local['order_date'].dt.date <= end_date)
    df_local = df_local[mask]
    
    # Terapkan filter nama produk
    if search_product:
        df_local = df_local[df_local['product_name'].str.contains(search_product, case=False, na=False)]

    # Agregasi: jumlah barang terbeli per produk
    agg_product = (
        df_local.groupby(['product_id', 'product_name'], as_index=False)
        .agg(items_terbeli=('quantity', 'sum'), pendapatan=('subtotal', 'sum'))
        .sort_values(['items_terbeli', 'pendapatan'], ascending=[False, False])
    )

    # Agregasi: tren harian (jumlah item dan pendapatan)
    daily = (
        df_local.assign(date=df_local['order_date'].dt.date)
        .groupby('date', as_index=False)
        .agg(items=('quantity', 'sum'), revenue=('subtotal', 'sum'))
        .sort_values('date')
    )

    # Metrik ringkasan
    total_items = int(agg_product['items_terbeli'].sum()) if not agg_product.empty else 0
    total_revenue = float(agg_product['pendapatan'].sum()) if not agg_product.empty else 0.0

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🧮 Total Item Terbeli", total_items)
    with col2:
        st.metric("💰 Total Pendapatan", f"Rp {total_revenue:,.2f}")

    # Chart: Top Produk berdasarkan Jumlah Terbeli
    st.markdown("### 📈 Top Produk berdasarkan Jumlah Terbeli")
    top_n = st.slider("Tampilkan Top N", min_value=5, max_value=50, value=10, step=5, key="order_top_n")
    st.bar_chart(agg_product.set_index('product_name')['items_terbeli'].head(top_n), use_container_width=True)

    # Chart: Tren Harian (Pembelian dan Pendapatan) - Side by Side
    st.markdown("### 📉 Tren Harian")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("**Pembelian (Jumlah Item)**")
        st.line_chart(daily.set_index('date')[['items']], use_container_width=True)
    
    with col_chart2:
        st.markdown("**Pendapatan**")
        st.line_chart(daily.set_index('date')[['revenue']], use_container_width=True)

    # Tabel: Rincian Order
    st.markdown("### 📋 Rincian Order (Item Level)")
    default_cols = [
        'order_detail_id', 'order_id', 'order_date', 'customer_name',
        'product_name', 'unit_price', 'quantity', 'subtotal', 'order_total'
    ]
    show_cols = st.multiselect(
        "Pilih Kolom Rincian",
        options=df_local.columns.tolist(),
        default=default_cols if all(c in df_local.columns for c in default_cols) else df_local.columns.tolist(),
        key="order_columns"
    )
    
    # Sorting dengan dropdown tunggal
    sort_options_order = []
    for col in df_local.columns:
        sort_options_order.append(f"{col} (ASC ↑)")
        sort_options_order.append(f"{col} (DESC ↓)")
    
    sort_selection_order = st.selectbox(
        "Urutkan berdasarkan",
        options=sort_options_order,
        index=sort_options_order.index("order_date (DESC ↓)") if "order_date (DESC ↓)" in sort_options_order else 0,
        key="order_sort"
    )
    
    # Parse selection
    sort_by_order = sort_selection_order.rsplit(" (", 1)[0]
    ascending_order = "ASC" in sort_selection_order
    sorted_order_df = df_local.sort_values(by=sort_by_order, ascending=ascending_order)
    
    st.dataframe(sorted_order_df[show_cols], use_container_width=True)

    # Export CSV
    @st.cache_data
    def convert_df_to_csv(_df):
        return _df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(sorted_order_df[show_cols])
    st.download_button(
        label="⬇️ Download Rincian Order CSV",
        data=csv,
        file_name='rincian_order.csv',
        mime='text/csv'
    )

# =====================================================
# FUNGSI: TAMPILAN PRODUK
# =====================================================
def tabelProducts_dan_chart():
    """Menampilkan produk dengan diagram batang penjualan"""
    
    df_prod = df_products.copy()
    if df_prod.empty:
        st.info("Belum ada data produk untuk ditampilkan.")
        return

    # Konversi tipe data
    df_prod['price'] = pd.to_numeric(df_prod['price'], errors='coerce')
    df_prod['stock'] = pd.to_numeric(df_prod['stock'], errors='coerce')

    # Hitung total terjual per produk dari order_details
    if not df_order_details.empty:
        df_sales = df_order_details.copy()
        df_sales['quantity'] = pd.to_numeric(df_sales['quantity'], errors='coerce').fillna(0).astype(int)
        df_sales['subtotal'] = pd.to_numeric(df_sales['subtotal'], errors='coerce')
        
        sales_summary = (
            df_sales.groupby(['product_id', 'product_name'], as_index=False)
            .agg(total_terjual=('quantity', 'sum'), total_pendapatan=('subtotal', 'sum'))
        )
        
        # Gabungkan dengan data produk
        df_prod = df_prod.merge(
            sales_summary[['product_id', 'total_terjual', 'total_pendapatan']],
            on='product_id',
            how='left'
        )
        df_prod['total_terjual'] = df_prod['total_terjual'].fillna(0).astype(int)
        df_prod['total_pendapatan'] = df_prod['total_pendapatan'].fillna(0)
    else:
        df_prod['total_terjual'] = 0
        df_prod['total_pendapatan'] = 0.0

    # Sidebar: Filter
    st.sidebar.header("Filter Produk")
    search_name = st.sidebar.text_input("Cari Nama Produk", value="", key="product_search_name")
    
    # Terapkan filter nama dulu
    df_filtered = df_prod.copy()
    if search_name:
        df_filtered = df_filtered[df_filtered['name'].str.contains(search_name, case=False, na=False)]
    
    # Hitung range harga dari data yang sudah difilter
    if not df_filtered.empty:
        price_min = float(df_filtered['price'].min())
        price_max = float(df_filtered['price'].max())
        
        # Hanya tampilkan slider jika ada range harga
        if price_max > price_min:
            price_range = st.sidebar.slider(
                "Rentang Harga",
                min_value=price_min,
                max_value=price_max,
                value=(price_min, price_max),
                key="product_price_range"
            )
            # Filter berdasarkan harga
            df_filtered = df_filtered[
                (df_filtered['price'] >= price_range[0]) & (df_filtered['price'] <= price_range[1])
            ]
        else:
            st.sidebar.info(f"Harga: Rp {price_min:,.2f}")

    # Metrik ringkasan
    total_products = len(df_filtered)
    total_stock = int(df_filtered['stock'].sum()) if not df_filtered.empty else 0
    total_sold = int(df_filtered['total_terjual'].sum()) if not df_filtered.empty else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Total Produk", total_products)
    with col2:
        st.metric("📊 Total Stok", total_stock)
    with col3:
        st.metric("🛒 Total Terjual", total_sold)

    # Diagram batang penjualan produk
    st.markdown("### 📊 Diagram Batang Penjualan Produk")
    
    if df_filtered.empty:
        st.warning("Tidak ada produk yang sesuai dengan filter.")
        return
    
    # Sort berdasarkan total terjual
    df_chart = df_filtered.sort_values('total_terjual', ascending=False)
    
    # Slider untuk memilih jumlah produk yang ditampilkan
    max_products = len(df_chart)
    if max_products > 1:
        top_n = st.slider(
            "Tampilkan Top N Produk Terlaris",
            min_value=1,
            max_value=min(max_products, 50),
            value=min(10, max_products),
            step=1,
            key="product_top_n"
        )
    else:
        top_n = max_products
    
    chart_data = df_chart.head(top_n).set_index('name')[['total_terjual']]
    st.bar_chart(chart_data, use_container_width=True)

    # Tabel detail produk
    st.markdown("### 📋 Tabel Detail Produk")
    show_cols = st.multiselect(
        "Pilih Kolom yang Ditampilkan",
        options=df_filtered.columns.tolist(),
        default=['product_id', 'name', 'price', 'stock', 'total_terjual', 'total_pendapatan'],
        key="product_columns"
    )
    
    if show_cols:
        # Sorting dengan dropdown tunggal
        sort_options_product = []
        for col in df_filtered.columns:
            sort_options_product.append(f"{col} (ASC ↑)")
            sort_options_product.append(f"{col} (DESC ↓)")
        
        sort_selection_product = st.selectbox(
            "Urutkan berdasarkan",
            options=sort_options_product,
            index=sort_options_product.index("total_terjual (DESC ↓)") if "total_terjual (DESC ↓)" in sort_options_product else 0,
            key="product_sort"
        )
        
        # Parse selection
        sort_by_product = sort_selection_product.rsplit(" (", 1)[0]
        ascending_product = "ASC" in sort_selection_product
        sorted_product_df = df_filtered.sort_values(by=sort_by_product, ascending=ascending_product)
        
        st.dataframe(
            sorted_product_df[show_cols],
            use_container_width=True
        )

        # Export CSV
        @st.cache_data
        def convert_df_to_csv(_df):
            return _df.to_csv(index=False).encode('utf-8')

        csv = convert_df_to_csv(sorted_product_df[show_cols])
        st.download_button(
            label="⬇️ Download Data Produk CSV",
            data=csv,
            file_name='data_produk.csv',
            mime='text/csv'
        )


# =====================================================
# SIDEBAR: NAVIGASI
# =====================================================
st.sidebar.success("Pilih Tabel:")
if st.sidebar.checkbox("Tampilkan Pelanggan"):
    tabelCustomers_dan_export()
if st.sidebar.checkbox("Tampilkan Produk"):
    tabelProducts_dan_chart()
if st.sidebar.checkbox("Tampilkan Order"):
    tabelOrders_dan_chart()