# Nama file: supermarket_sales_etl_star_schema_dag_v4.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

# Path direktori data
BASE_DIR = "/root/airflow/data" 
INPUT_FILE = os.path.join(BASE_DIR, "supermarket_sales.csv") 
CLEANED_FILE = os.path.join(BASE_DIR, "supermarket_sales_clean.csv")

OUTPUT_STAR_SCHEMA_DIR = os.path.join(BASE_DIR, "output_star_schema")
os.makedirs(OUTPUT_STAR_SCHEMA_DIR, exist_ok=True)

# Path masing-masing file output
DIM_PRODUCT_LINE_FILE = os.path.join(OUTPUT_STAR_SCHEMA_DIR, "dim_product_line.csv")
DIM_BRANCH_FILE = os.path.join(OUTPUT_STAR_SCHEMA_DIR, "dim_branch.csv")
DIM_DATE_FILE = os.path.join(OUTPUT_STAR_SCHEMA_DIR, "dim_date.csv")
DIM_PAYMENT_METHOD_FILE = os.path.join(OUTPUT_STAR_SCHEMA_DIR, "dim_payment_method.csv")
DIM_CUSTOMER_TYPE_FILE = os.path.join(OUTPUT_STAR_SCHEMA_DIR, "dim_customer_type.csv")
DIM_GENDER_FILE = os.path.join(OUTPUT_STAR_SCHEMA_DIR, "dim_gender.csv")
FACT_SALES_FILE = os.path.join(OUTPUT_STAR_SCHEMA_DIR, "fact_sales.csv")
FACT_PRODUCT_PERFORM_FILE = os.path.join(OUTPUT_STAR_SCHEMA_DIR, "fact_product_perform.csv")
FACT_CUSTOMER_BEHAVIOR_FILE = os.path.join(OUTPUT_STAR_SCHEMA_DIR, "fact_customer_behavior.csv")

# Extract & Clean
def extract_and_clean_data():
    df = pd.read_csv(INPUT_FILE)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date', 'Branch', 'City', 'Product line', 'Unit price', 'Quantity', 'Payment', 'cogs', 'Rating', 'Gender'], inplace=True)
    df.rename(columns={
        'Date': 'tanggal_transaksi',
        'Branch': 'cabang',
        'City': 'kota',
        'Customer type': 'tipe_pelanggan',
        'Gender': 'gender',
        'Product line': 'lini_produk',
        'Unit price': 'harga_satuan',
        'Quantity': 'kuantitas',
        'Payment': 'metode_pembayaran',
        'cogs': 'biaya_pokok_penjualan',
        'Rating': 'rating_produk'
    }, inplace=True)
    df.to_csv(CLEANED_FILE, index=False)

# Transform + Load
def transform_to_dimensions_and_facts():
    df = pd.read_csv(CLEANED_FILE, parse_dates=['tanggal_transaksi'])

    # Dimensi Date
    dim_date = df[['tanggal_transaksi']].drop_duplicates().reset_index(drop=True)
    dim_date['date_id'] = dim_date.index + 1
    dim_date['full_date'] = dim_date['tanggal_transaksi'].dt.date
    dim_date['day'] = dim_date['tanggal_transaksi'].dt.day
    dim_date['month'] = dim_date['tanggal_transaksi'].dt.month
    dim_date['year'] = dim_date['tanggal_transaksi'].dt.year
    dim_date.rename(columns={'tanggal_transaksi': 'date_time'}, inplace=True)
    dim_date = dim_date[['date_id', 'date_time', 'full_date', 'day', 'month', 'year']]
    dim_date.to_csv(DIM_DATE_FILE, index=False)

    # Dimensi Product Line
    dim_product_line = df[['lini_produk']].drop_duplicates().reset_index(drop=True)
    dim_product_line['product_line_id'] = dim_product_line.index + 1
    dim_product_line.rename(columns={'lini_produk': 'product_line_name'}, inplace=True)
    dim_product_line.to_csv(DIM_PRODUCT_LINE_FILE, index=False)

    # Dimensi Branch
    dim_branch = df[['cabang', 'kota']].drop_duplicates(subset=['cabang']).reset_index(drop=True)
    dim_branch['branch_id'] = dim_branch.index + 1
    dim_branch.rename(columns={'cabang': 'branch_name', 'kota': 'city'}, inplace=True)
    dim_branch.to_csv(DIM_BRANCH_FILE, index=False)

    # Dimensi Payment Method
    dim_payment_method = df[['metode_pembayaran']].drop_duplicates().reset_index(drop=True)
    dim_payment_method['payment_method_id'] = dim_payment_method.index + 1
    dim_payment_method.rename(columns={'metode_pembayaran': 'payment_type'}, inplace=True)
    dim_payment_method.to_csv(DIM_PAYMENT_METHOD_FILE, index=False)

    # Dimensi Customer Type
    dim_customer_type = df[['tipe_pelanggan']].drop_duplicates().reset_index(drop=True)
    dim_customer_type['customer_type_id'] = dim_customer_type.index + 1
    dim_customer_type.rename(columns={'tipe_pelanggan': 'customer_type_name'}, inplace=True)
    dim_customer_type.to_csv(DIM_CUSTOMER_TYPE_FILE, index=False)

    # Dimensi Gender (tambahan)
    dim_gender = df[['gender']].drop_duplicates().reset_index(drop=True)
    dim_gender['gender_id'] = dim_gender.index + 1
    dim_gender.to_csv(DIM_GENDER_FILE, index=False)

    # Merge FK ke df_fact
    df_fact = df.copy()
    df_fact['full_date_for_join'] = df_fact['tanggal_transaksi'].dt.date
    df_fact = pd.merge(df_fact, dim_date[['date_id', 'full_date']], left_on='full_date_for_join', right_on='full_date', how='left')
    df_fact = pd.merge(df_fact, dim_product_line[['product_line_id', 'product_line_name']], left_on='lini_produk', right_on='product_line_name', how='left')
    df_fact = pd.merge(df_fact, dim_branch[['branch_id', 'branch_name', 'city']], left_on=['cabang', 'kota'], right_on=['branch_name', 'city'], how='left')
    df_fact = pd.merge(df_fact, dim_payment_method[['payment_method_id', 'payment_type']], left_on='metode_pembayaran', right_on='payment_type', how='left')
    df_fact = pd.merge(df_fact, dim_customer_type[['customer_type_id', 'customer_type_name']], left_on='tipe_pelanggan', right_on='customer_type_name', how='left')
    df_fact = pd.merge(df_fact, dim_gender[['gender_id', 'gender']], left_on='gender', right_on='gender', how='left')

    # fact_sales
    fact_sales = df_fact[['date_id', 'branch_id', 'product_line_id', 'payment_method_id', 'customer_type_id', 'harga_satuan', 'kuantitas', 'biaya_pokok_penjualan', 'rating_produk']].copy()
    fact_sales.rename(columns={
        'harga_satuan': 'unit_price',
        'kuantitas': 'quantity',
        'biaya_pokok_penjualan': 'cogs',
        'rating_produk': 'rating'
    }, inplace=True)
    fact_sales.insert(0, 'sales_id', range(1, 1 + len(fact_sales))) 
    fact_sales.to_csv(FACT_SALES_FILE, index=False)

    # fact_product_perform
    fact_product_perform = df_fact[['product_line_id', 'branch_id', 'date_id', 'harga_satuan', 'kuantitas', 'biaya_pokok_penjualan', 'rating_produk']].copy()
    fact_product_perform.rename(columns={
        'harga_satuan': 'unit_price',
        'kuantitas': 'quantity',
        'biaya_pokok_penjualan': 'cogs',
        'rating_produk': 'rating'
    }, inplace=True)
    fact_product_perform.insert(0, 'product_perform_id', range(1, 1 + len(fact_product_perform))) 
    fact_product_perform.to_csv(FACT_PRODUCT_PERFORM_FILE, index=False)

    # fact_customer_behavior (fix schema sesuai model Django)
    fact_customer_behavior = df_fact[['date_id', 'branch_id', 'customer_type_id', 'gender_id', 'kuantitas', 'biaya_pokok_penjualan', 'rating_produk']].copy()
    fact_customer_behavior.rename(columns={
        'kuantitas': 'quantity',
        'biaya_pokok_penjualan': 'cogs',
        'rating_produk': 'rating'
    }, inplace=True)
    fact_customer_behavior.insert(0, 'customer_behavior_id', range(1, 1 + len(fact_customer_behavior)))
    fact_customer_behavior.to_csv(FACT_CUSTOMER_BEHAVIOR_FILE, index=False)

# Load verifikasi
def verify_load():
    print("ETL selesai. Semua file star schema termasuk FactCustomerBehavior berhasil dibuat dengan schema yang benar.")

# DAG
with DAG(
    dag_id="supermarket_sales_etl_star_schema_v4", 
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["supermarket_sales", "etl", "star_schema"]
) as dag:
    t1 = PythonOperator(task_id="extract_and_clean", python_callable=extract_and_clean_data)
    t2 = PythonOperator(task_id="transform_star_schema", python_callable=transform_to_dimensions_and_facts)
    t3 = PythonOperator(task_id="verify_load", python_callable=verify_load)
    t1 >> t2 >> t3
