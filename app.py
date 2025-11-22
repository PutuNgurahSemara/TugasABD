# Import library
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
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
# FUNGSI: DASHBOARD UTAMA
# =====================================================
def dashboard_utama():
    """Menampilkan dashboard utama dengan berbagai visualisasi"""
    
    # Header
    st.title("🎓 Tugas Praktikum ABD ASIK")
    st.markdown("---")
    st.image("peakpx.jpg", caption="Gambar tambahan ga tau fungsinya apaan")
    # Dropdown untuk memilih jenis visualisasi
    st.subheader("📊 Pilih Jenis Visualisasi")
    visualization_type = st.selectbox(
        "Pilih tipe chart yang ingin ditampilkan:",
        ["Pie Chart", "Area Chart", "Bar Chart", "Line Chart", "Map (Geographic)"],
        key="viz_type"
    )
    
    st.markdown("---")
    
    # PIE CHART
    if visualization_type == "Pie Chart":
        st.header("🥧 Pie Chart - Distribusi Produk Berdasarkan Kategori Harga")
        st.markdown("""
        **Deskripsi:** Pie chart ini menampilkan distribusi produk berdasarkan kategori harga.
        Produk dikategorikan menjadi Low, Medium, High, dan Premium berdasarkan harga jualnya.
        Visualisasi ini membantu memahami komposisi produk di toko berdasarkan segmen harga.
        """)
        
        # Kategorisasi produk berdasarkan harga
        df_prod = df_products.copy()
        df_prod['price'] = pd.to_numeric(df_prod['price'], errors='coerce')
        
        # Buat kategori harga
        df_prod['price_category'] = pd.cut(df_prod['price'], 
                                            bins=[0, 30000, 60000, 80000, float('inf')],
                                            labels=['Low (< 30k)', 'Medium (30k-60k)', 'High (60k-80k)', 'Premium (> 80k)'])
        
        category_counts = df_prod['price_category'].value_counts()
        
        # Buat pie chart dengan Plotly (INTERAKTIF)
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title='Distribusi Produk Berdasarkan Kategori Harga',
            color_discrete_sequence=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'],
            hole=0.3  # Donut chart
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>'
        )
        fig.update_layout(
            height=500,
            font=dict(size=14),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tampilkan statistik
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Produk", len(df_prod))
        with col2:
            most_common = category_counts.index[0]
            st.metric("Kategori Terbanyak", most_common)
        with col3:
            avg_price = df_prod['price'].mean()
            st.metric("Rata-rata Harga", f"Rp {avg_price:,.0f}")
    
    # AREA CHART
    elif visualization_type == "Area Chart":
        st.header("📈 Area Chart - Tren Pendapatan Harian")
        st.markdown("""
        **Deskripsi:** Area chart ini menunjukkan tren pendapatan dari waktu ke waktu.
        Setiap titik merepresentasikan total pendapatan per hari, dan area yang terisi
        memberikan visualisasi kumulatif yang mudah dibaca. Berguna untuk melihat
        pola penjualan dan mengidentifikasi periode puncak atau penurunan.
        """)
        
        if not df_order_details.empty:
            df_orders = df_order_details.copy()
            df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
            df_orders['subtotal'] = pd.to_numeric(df_orders['subtotal'], errors='coerce')
            
            # Agregasi pendapatan per hari
            daily_revenue = df_orders.groupby(df_orders['order_date'].dt.date)['subtotal'].sum().reset_index()
            daily_revenue.columns = ['Date', 'Revenue']
            daily_revenue = daily_revenue.sort_values('Date')
            
            # Buat area chart dengan Plotly (INTERAKTIF)
            fig = px.area(
                daily_revenue,
                x='Date',
                y='Revenue',
                title='Tren Pendapatan Harian',
                labels={'Revenue': 'Pendapatan (Rp)', 'Date': 'Tanggal'}
            )
            fig.update_traces(
                line_color='#0d47a1',
                fillcolor='rgba(31, 119, 180, 0.3)',
                hovertemplate='<b>Tanggal:</b> %{x}<br><b>Pendapatan:</b> Rp %{y:,.0f}<extra></extra>'
            )
            fig.update_layout(
                height=500,
                hovermode='x unified',
                xaxis_title='Tanggal',
                yaxis_title='Pendapatan (Rp)',
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistik
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_rev = daily_revenue['Revenue'].sum()
                st.metric("Total Pendapatan", f"Rp {total_rev:,.0f}")
            with col2:
                avg_rev = daily_revenue['Revenue'].mean()
                st.metric("Rata-rata/Hari", f"Rp {avg_rev:,.0f}")
            with col3:
                max_rev = daily_revenue['Revenue'].max()
                st.metric("Pendapatan Tertinggi", f"Rp {max_rev:,.0f}")
            with col4:
                days = len(daily_revenue)
                st.metric("Hari Transaksi", f"{days} hari")
        else:
            st.warning("Tidak ada data order untuk ditampilkan.")
    
    # BAR CHART
    elif visualization_type == "Bar Chart":
        st.header("📊 Bar Chart - Top 15 Produk Terlaris")
        st.markdown("""
        **Deskripsi:** Bar chart horizontal ini menampilkan 15 produk dengan penjualan tertinggi
        berdasarkan jumlah unit terjual. Setiap bar merepresentasikan satu produk, dengan
        panjang bar menunjukkan volume penjualan. Visualisasi ini memudahkan identifikasi
        produk best-seller dan membantu strategi inventory management.
        """)
        
        if not df_order_details.empty:
            df_sales = df_order_details.copy()
            df_sales['quantity'] = pd.to_numeric(df_sales['quantity'], errors='coerce').fillna(0)
            
            # Agregasi penjualan per produk
            product_sales = df_sales.groupby('product_name')['quantity'].sum().sort_values(ascending=True).tail(15).reset_index()
            product_sales.columns = ['Product', 'Quantity']
            
            # Buat bar chart horizontal dengan Plotly (INTERAKTIF)
            fig = px.bar(
                product_sales,
                x='Quantity',
                y='Product',
                orientation='h',
                title='Top 15 Produk Terlaris',
                labels={'Quantity': 'Jumlah Terjual (Unit)', 'Product': 'Nama Produk'},
                color='Quantity',
                color_continuous_scale='Viridis'
            )
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>Terjual: %{x:,} unit<extra></extra>'
            )
            fig.update_layout(
                height=600,
                showlegend=False,
                xaxis_title='Jumlah Terjual (Unit)',
                yaxis_title='Nama Produk',
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistik
            col1, col2, col3 = st.columns(3)
            with col1:
                total_sold = df_sales['quantity'].sum()
                st.metric("Total Unit Terjual", f"{int(total_sold):,}")
            with col2:
                best_seller = product_sales.index[-1]
                st.metric("Best Seller", best_seller)
            with col3:
                best_qty = product_sales.values[-1]
                st.metric("Terjual", f"{int(best_qty):,} unit")
        else:
            st.warning("Tidak ada data penjualan untuk ditampilkan.")
    
    # LINE CHART
    elif visualization_type == "Line Chart":
        st.header("📉 Line Chart - Tren Jumlah Order Per Hari")
        st.markdown("""
        **Deskripsi:** Line chart ini menampilkan tren jumlah order yang masuk per hari.
        Setiap titik pada garis merepresentasikan total order dalam satu hari.
        Visualisasi ini berguna untuk menganalisis pola pemesanan, mengidentifikasi
        hari-hari sibuk, dan merencanakan kapasitas operasional.
        """)
        
        if not df_order_details.empty:
            df_orders = df_order_details.copy()
            df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
            
            # Hitung jumlah order per hari
            daily_orders = df_orders.groupby(df_orders['order_date'].dt.date)['order_id'].nunique().reset_index()
            daily_orders.columns = ['Date', 'Orders']
            daily_orders = daily_orders.sort_values('Date')
            
            # Buat line chart dengan Plotly (INTERAKTIF)
            fig = px.line(
                daily_orders,
                x='Date',
                y='Orders',
                title='Tren Jumlah Order Per Hari',
                labels={'Orders': 'Jumlah Order', 'Date': 'Tanggal'},
                markers=True
            )
            fig.update_traces(
                line_color='#d32f2f',
                marker=dict(size=8),
                hovertemplate='<b>Tanggal:</b> %{x}<br><b>Jumlah Order:</b> %{y}<extra></extra>'
            )
            fig.update_layout(
                height=500,
                hovermode='x unified',
                xaxis_title='Tanggal',
                yaxis_title='Jumlah Order',
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistik
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_orders = df_orders['order_id'].nunique()
                st.metric("Total Order", f"{total_orders:,}")
            with col2:
                avg_orders = daily_orders['Orders'].mean()
                st.metric("Rata-rata/Hari", f"{avg_orders:.1f}")
            with col3:
                max_orders = daily_orders['Orders'].max()
                st.metric("Order Terbanyak", f"{int(max_orders)}")
            with col4:
                active_days = len(daily_orders)
                st.metric("Hari Aktif", f"{active_days} hari")
        else:
            st.warning("Tidak ada data order untuk ditampilkan.")
    
    # MAP (GEOGRAPHIC)
    elif visualization_type == "Map (Geographic)":
        st.header("🗺️ Map - Distribusi Pelanggan Berdasarkan Lokasi")
        st.markdown("""
        **Deskripsi:** Visualisasi geografis ini menampilkan distribusi pelanggan berdasarkan
        lokasi atau wilayah. Dalam implementasi ini, kami menampilkan bar chart untuk
        distribusi berdasarkan kota (karena data GPS tidak tersedia). Visualisasi ini
        membantu memahami jangkauan geografis bisnis dan area potensial untuk ekspansi.
        """)
        
        if not df_customers.empty:
            # Ekstrak informasi kota dari alamat (simulasi)
            df_cust = df_customers.copy()
            
            # Simulasi: buat kategori wilayah berdasarkan pattern alamat
            import random
            cities = ['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Semarang', 'Makassar', 'Palembang', 'Denpasar']
            df_cust['city'] = [random.choice(cities) for _ in range(len(df_cust))]
            
            city_counts = df_cust['city'].value_counts().sort_values(ascending=True).reset_index()
            city_counts.columns = ['City', 'Count']
            
            # Buat bar chart untuk distribusi kota dengan Plotly (INTERAKTIF)
            fig = px.bar(
                city_counts,
                x='Count',
                y='City',
                orientation='h',
                title='Distribusi Pelanggan Berdasarkan Kota',
                labels={'Count': 'Jumlah Pelanggan', 'City': 'Kota'},
                color='Count',
                color_continuous_scale='Teal'
            )
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>Pelanggan: %{x:,} orang<extra></extra>'
            )
            fig.update_layout(
                height=500,
                showlegend=False,
                xaxis_title='Jumlah Pelanggan',
                yaxis_title='Kota',
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistik
            col1, col2, col3 = st.columns(3)
            with col1:
                total_cust = len(df_cust)
                st.metric("Total Pelanggan", f"{total_cust:,}")
            with col2:
                num_cities = len(city_counts)
                st.metric("Jangkauan Kota", f"{num_cities} kota")
            with col3:
                top_city = city_counts.index[-1]
                st.metric("Kota Terbanyak", top_city)
            
            st.info("💡 **Catatan:** Data geografis ini adalah simulasi untuk tujuan demonstrasi. Dalam implementasi nyata, gunakan koordinat GPS untuk visualisasi peta interaktif.")
        else:
            st.warning("Tidak ada data pelanggan untuk ditampilkan.")

# =====================================================
# SIDEBAR: NAVIGASI
# =====================================================
st.sidebar.title("🧭 Navigasi")
st.sidebar.markdown("---")

menu_option = st.sidebar.radio(
    "Pilih Menu:",
    ["Dashboard Utama", "Data Pelanggan", "Data Produk", "Data Order"],
    key="main_menu"
)

st.sidebar.markdown("---")
st.sidebar.info("**Tugas Praktikum ABD**\n\nStreamlit Dashboard v1.0")

# Routing menu
if menu_option == "Dashboard Utama":
    dashboard_utama()
elif menu_option == "Data Pelanggan":
    tabelCustomers_dan_export()
elif menu_option == "Data Produk":
    tabelProducts_dan_chart()
elif menu_option == "Data Order":
    tabelOrders_dan_chart()