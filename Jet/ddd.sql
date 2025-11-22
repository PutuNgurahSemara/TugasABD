
-- Tabel customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    birthdate DATE
);

COMMENT ON COLUMN customers.birthdate IS 'Tanggal lahir pelanggan';

-- 🔍 Index tambahan
-- Index untuk pencarian cepat berdasarkan nama pelanggan (misal saat filter nama di Streamlit)
CREATE INDEX idx_customers_name ON customers (name);
-- Index untuk pencarian/filter berdasarkan tanggal lahir (jika digunakan analisis umur pelanggan)
CREATE INDEX idx_customers_birthdate ON customers (birthdate);


-- Tabel products
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock INT NOT NULL
);

-- 🔍 Index tambahan
-- Untuk pencarian cepat produk berdasarkan nama (misal fitur filter di dashboard)
CREATE INDEX idx_products_name ON products (name);
-- Untuk analisis harga produk (misal histogram harga)
CREATE INDEX idx_products_price ON products (price);

-- Tabel orders
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, --jika tidak diisi, otomatis berisi waktu saat data dimasukkan ke tabel.
    total_amount NUMERIC(10, 2) NOT NULL,
    CONSTRAINT fk_customer --memberi nama aturan relasi (boleh kamu ganti).
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id) --jika data pelanggan dihapus dari tabel customers
        ON DELETE CASCADE
);

-- 🔍 Index tambahan
-- Untuk analisis waktu penjualan (misal line chart penjualan per bulan)
CREATE INDEX idx_orders_order_date ON orders (order_date);
-- Untuk join cepat dengan tabel customers
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
-- Untuk agregasi berdasarkan total_amount
CREATE INDEX idx_orders_total_amount ON orders (total_amount);

-- Tabel order_details
CREATE TABLE IF NOT EXISTS order_details (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) GENERATED ALWAYS AS (quantity * price) STORED, -- hasil quantity * price, GENERATED ALWAYS AS (...) STORED kolom ini selalu dihitung dan disimpan di database
    CONSTRAINT fk_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);

-- 🔍 Index tambahan
-- Untuk join cepat antara order_details ↔ orders
CREATE INDEX idx_order_details_order_id ON order_details (order_id);
-- Untuk join cepat antara order_details ↔ products
CREATE INDEX idx_order_details_product_id ON order_details (product_id);
-- Untuk analisis jumlah barang terjual
CREATE INDEX idx_order_details_quantity ON order_details (quantity);
-- Untuk analisis harga per produk di detail pesanan
CREATE INDEX idx_order_details_price ON order_details (price);


INSERT INTO customers (name, email, phone, address, birthdate) VALUES
('Andi Pratama', 'andi@example.com', '081234567890', 'Jl. Mawar No. 21', '1995-03-12'),
('Budi Setiawan', 'budi@example.com', '081298765432', 'Jl. Melati No. 14', '1988-07-05'),
('Citra Lestari', 'citra@example.com', '082134567890', 'Jl. Kenanga No. 9', '1999-11-23');

INSERT INTO products (name, description, price, stock) VALUES
('Kopi Arabika', 'Kopi arabika premium 250g', 75000, 30),
('Teh Hijau', 'Teh hijau organik 100g', 45000, 50),
('Cokelat Bubuk', 'Coklat bubuk premium 200g', 65000, 40),
('Gula Aren', 'Gula aren kemasan 500g', 30000, 25);


INSERT INTO orders (customer_id, order_date, total_amount) VALUES
(1, '2025-01-10 10:15:00', 150000),
(2, '2025-02-02 14:20:00', 95000),
(3, '2025-02-15 09:45:00', 180000);

INSERT INTO order_details (order_id, product_id, quantity, price) VALUES
(1, 1, 2, 75000),   -- 2 × Kopi Arabika
(1, 4, 1, 30000),   -- 1 × Gula Aren

(2, 2, 1, 45000),   -- 1 × Teh Hijau
(2, 4, 1, 30000),   -- 1 × Gula Aren

(3, 1, 1, 75000),   -- 1 × Kopi
(3, 3, 2, 65000);   -- 2 × Coklat Bubuk

-- MEnambahkan data hingga 100 data per tabel

INSERT INTO customers (name, email, phone, address, birthdate)
SELECT
    'Customer ' || g AS name,
    'customer' || g || '@example.com' AS email,
    '08' || floor(random()*1000000000)::TEXT AS phone,
    'Alamat No. ' || g AS address,
    date '1970-01-01' + (random()*15000)::int * interval '1 day'
FROM generate_series(4, 100) g;

INSERT INTO products (name, description, price, stock)
SELECT
    'Produk ' || g,
    'Deskripsi produk ' || g,
    (random() * 90000 + 10000)::numeric(10,2),  -- harga 10k – 100k
    (random() * 80 + 10)::int                  -- stok 10–90
FROM generate_series(5, 100) g;


INSERT INTO orders (customer_id, order_date, total_amount)
SELECT
    (random() * 99 + 1)::int AS customer_id,
    NOW() - (random() * 365 || ' days')::interval AS order_date,
    (random() * 500000 + 50000)::numeric(10,2)
FROM generate_series(4, 100);

INSERT INTO order_details (order_id, product_id, quantity, price)
SELECT
    (random() * 99 + 1)::int AS order_id,
    (random() * 99 + 1)::int AS product_id,
    (random() * 4 + 1)::int AS quantity,          -- 1–5 pcs
    (random() * 90000 + 10000)::numeric(10,2)     -- harga 10k–100k
FROM generate_series(1, 100);
