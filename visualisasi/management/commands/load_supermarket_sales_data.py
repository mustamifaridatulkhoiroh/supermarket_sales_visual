import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import os

from visualisasi.models import (
    DimDate, DimProductLine, DimBranch, DimPaymentMethod, 
    DimCustomerType, DimGender,
    FactSales, FactProductPerform, FactCustomerBehavior
)

class Command(BaseCommand):
    help = 'Load data star schema supermarket dari CSV ke database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS(" Memulai proses load data star schema supermarket..."))

        CSV_DIR = "/root/airflow/data/output_star_schema"

        # Safe Delete Existing Data
        with transaction.atomic():
            self.stdout.write("Menghapus data lama...")
            FactSales.objects.all().delete()
            FactProductPerform.objects.all().delete()
            FactCustomerBehavior.objects.all().delete()
            DimCustomerType.objects.all().delete()
            DimPaymentMethod.objects.all().delete()
            DimGender.objects.all().delete()
            DimBranch.objects.all().delete()
            DimProductLine.objects.all().delete()
            DimDate.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(" Data lama berhasil dihapus."))

        try:
            # DIM DATE
            df_date = pd.read_csv(os.path.join(CSV_DIR, 'dim_date.csv'), parse_dates=['date_time'])
            DimDate.objects.bulk_create([
                DimDate(
                    date_id=row['date_id'],
                    date_time=timezone.make_aware(row['date_time']) if row['date_time'].tzinfo is None else row['date_time'],
                    full_date=row['full_date'],
                    day=row['day'],
                    month=row['month'],
                    year=row['year']
                ) for _, row in df_date.iterrows()
            ])
            self.stdout.write(self.style.SUCCESS(f"{len(df_date)} data tanggal dimuat."))

            # DIM PRODUCT LINE
            df_product_line = pd.read_csv(os.path.join(CSV_DIR, 'dim_product_line.csv'))
            DimProductLine.objects.bulk_create([
                DimProductLine(
                    product_line_id=row['product_line_id'],
                    product_line_name=row['product_line_name']
                ) for _, row in df_product_line.iterrows()
            ])
            self.stdout.write(self.style.SUCCESS(f"{len(df_product_line)} data product line dimuat."))

            # DIM BRANCH
            df_branch = pd.read_csv(os.path.join(CSV_DIR, 'dim_branch.csv'))
            DimBranch.objects.bulk_create([
                DimBranch(
                    branch_id=row['branch_id'],
                    branch_name=row['branch_name'],
                    city=row['city']
                ) for _, row in df_branch.iterrows()
            ])
            self.stdout.write(self.style.SUCCESS(f"{len(df_branch)} data branch dimuat."))

            # DIM PAYMENT METHOD
            df_payment = pd.read_csv(os.path.join(CSV_DIR, 'dim_payment_method.csv'))
            DimPaymentMethod.objects.bulk_create([
                DimPaymentMethod(
                    payment_method_id=row['payment_method_id'],
                    payment_type=row['payment_type']
                ) for _, row in df_payment.iterrows()
            ])
            self.stdout.write(self.style.SUCCESS(f"{len(df_payment)} data payment method dimuat."))

            # DIM CUSTOMER TYPE
            df_customer_type = pd.read_csv(os.path.join(CSV_DIR, 'dim_customer_type.csv'))
            DimCustomerType.objects.bulk_create([
                DimCustomerType(
                    customer_type_id=row['customer_type_id'],
                    customer_type=row['customer_type_name']
                ) for _, row in df_customer_type.iterrows()
            ])
            self.stdout.write(self.style.SUCCESS(f"{len(df_customer_type)} data customer type dimuat."))

            # DIM GENDER (opsional jika memang ada)
            gender_file = os.path.join(CSV_DIR, 'dim_gender.csv')
            if os.path.exists(gender_file):
                df_gender = pd.read_csv(gender_file)
                DimGender.objects.bulk_create([
                    DimGender(
                        gender_id=row['gender_id'],
                        gender=row['gender']
                    ) for _, row in df_gender.iterrows()
                ])
                self.stdout.write(self.style.SUCCESS(f"{len(df_gender)} data gender dimuat."))

            # Membuat Mapping ID ke Object
            dim_date_map = {d.date_id: d for d in DimDate.objects.all()}
            dim_branch_map = {b.branch_id: b for b in DimBranch.objects.all()}
            dim_product_line_map = {pl.product_line_id: pl for pl in DimProductLine.objects.all()}
            dim_payment_map = {p.payment_method_id: p for p in DimPaymentMethod.objects.all()}
            dim_customer_type_map = {c.customer_type_id: c for c in DimCustomerType.objects.all()}
            dim_gender_map = {g.gender_id: g for g in DimGender.objects.all()}

            # FACT SALES
            df_sales = pd.read_csv(os.path.join(CSV_DIR, 'fact_sales.csv'))
            FactSales.objects.bulk_create([
                FactSales(
                    date=dim_date_map[row['date_id']],
                    branch=dim_branch_map[row['branch_id']],
                    product_line=dim_product_line_map[row['product_line_id']],
                    payment_method=dim_payment_map[row['payment_method_id']],
                    customer_type=dim_customer_type_map[row['customer_type_id']],
                    unit_price=row['unit_price'],
                    quantity=row['quantity'],
                    cogs=row['cogs'],
                    rating=row['rating']
                ) for _, row in df_sales.iterrows()
            ])
            self.stdout.write(self.style.SUCCESS(f"{len(df_sales)} data fact sales dimuat."))

            # FACT PRODUCT PERFORM
            df_product_perform = pd.read_csv(os.path.join(CSV_DIR, 'fact_product_perform.csv'))
            FactProductPerform.objects.bulk_create([
                FactProductPerform(
                    product_line=dim_product_line_map[row['product_line_id']],
                    branch=dim_branch_map[row['branch_id']],
                    date=dim_date_map[row['date_id']],
                    unit_price=row['unit_price'],
                    quantity=row['quantity'],
                    cogs=row['cogs'],
                    rating=row['rating']
                ) for _, row in df_product_perform.iterrows()
            ])
            self.stdout.write(self.style.SUCCESS(f"{len(df_product_perform)} data fact product perform dimuat."))

            # FACT CUSTOMER BEHAVIOR
            df_behavior = pd.read_csv(os.path.join(CSV_DIR, 'fact_customer_behavior.csv'))
            FactCustomerBehavior.objects.bulk_create([
                FactCustomerBehavior(
                    date=dim_date_map[row['date_id']],
                    customer_type=dim_customer_type_map[row['customer_type_id']],
                    gender=dim_gender_map.get(row['gender_id']),  # Optional, pakai .get untuk handle None
                    branch=dim_branch_map[row['branch_id']],
                    quantity=row['quantity'],
                    cogs=row['cogs'],
                    rating=row['rating']
                ) for _, row in df_behavior.iterrows()
            ])
            self.stdout.write(self.style.SUCCESS(f"{len(df_behavior)} data fact customer behavior dimuat."))

            self.stdout.write(self.style.SUCCESS("🎉 SEMUA DATA BERHASIL DIMUAT!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Terjadi error fatal: {e}"))
