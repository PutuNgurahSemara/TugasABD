"""Script untuk export data dari database ke CSV"""
from config import *
import pandas as pd
import os

# Buat folder data jika belum ada
os.makedirs('data', exist_ok=True)

print("Mengekspor data dari database...")

# Export customers
df_customers = pd.DataFrame(view_customers(), columns=[
    'customer_id', 'name', 'email', 'phone', 'address', 'birthdate'
])
df_customers.to_csv('data/customers.csv', index=False)
print(f"✓ Customers: {len(df_customers)} records exported")

# Export products
df_products = pd.DataFrame(view_products(), columns=[
    'product_id', 'name', 'description', 'price', 'stock'
])
df_products.to_csv('data/products.csv', index=False)
print(f"✓ Products: {len(df_products)} records exported")

# Export order details
df_order_details = pd.DataFrame(view_order_details_with_info(), columns=[
    'order_detail_id', 'order_id', 'order_date', 'customer_id', 'customer_name',
    'product_id', 'product_name', 'unit_price', 'quantity', 'subtotal',
    'order_total', 'phone'
])
df_order_details.to_csv('data/order_details.csv', index=False)
print(f"✓ Order Details: {len(df_order_details)} records exported")

print("\n✅ Semua data berhasil di-export ke folder 'data/'!")
