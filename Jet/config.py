import psycopg2

# Koneksi ke database PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",          # port default PostgreSQL
    user="postgres",      # ganti sesuai user PostgreSQL kamu
    password="putu2520",  # ganti sesuai password PostgreSQL kamu
    dbname="jets"         # nama database
)

print("Koneksi PostgreSQL berhasil!")

# Membuat cursor
c = conn.cursor()

# ============================
# Fungsi ambil data dari tabel
# ============================

def view_customers():
    query = '''
        SELECT customer_id, name, email, phone, address, birthdate
        FROM customers
        ORDER BY name ASC
    '''
    c.execute(query)
    return c.fetchall()

def view_orders_with_customers():
    query = '''
        SELECT 
            o.order_id, 
            o.order_date, 
            o.total_amount, 
            c.name AS customer_name, 
            c.phone 
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC
    '''
    c.execute(query)
    return c.fetchall()

def view_products():
    query = '''
        SELECT product_id, name, description, price, stock
        FROM products
        ORDER BY name ASC
    '''
    c.execute(query)
    return c.fetchall()

def view_order_details_with_info():
    query = '''
        SELECT 
            od.order_detail_id,
            o.order_id,
            o.order_date,
            c.customer_id,
            c.name AS customer_name,
            p.product_id,
            p.name AS product_name,
            p.price AS unit_price,
            od.quantity,
            od.subtotal,
            o.total_amount AS order_total,
            c.phone
        FROM order_details od
        JOIN orders o ON od.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products p ON od.product_id = p.product_id
        ORDER BY o.order_date DESC
    '''
    c.execute(query)
    return c.fetchall()


    # Tutup koneksi
    c.close()
    conn.close()