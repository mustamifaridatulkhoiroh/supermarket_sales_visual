# Generated by Django 4.2.21 on 2025-06-13 05:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DimBranch',
            fields=[
                ('branch_id', models.IntegerField(primary_key=True, serialize=False)),
                ('branch_name', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Dimensi Cabang',
                'verbose_name_plural': 'Dimensi Cabang',
                'db_table': 'dim_branch',
                'ordering': ['branch_name'],
            },
        ),
        migrations.CreateModel(
            name='DimCustomerType',
            fields=[
                ('customer_type_id', models.IntegerField(primary_key=True, serialize=False)),
                ('customer_type', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Dimensi Tipe Pelanggan',
                'verbose_name_plural': 'Dimensi Tipe Pelanggan',
                'db_table': 'dim_customer_type',
                'ordering': ['customer_type'],
            },
        ),
        migrations.CreateModel(
            name='DimDate',
            fields=[
                ('date_id', models.IntegerField(primary_key=True, serialize=False)),
                ('date_time', models.DateTimeField(db_column='date_time')),
                ('full_date', models.DateField(unique=True)),
                ('day', models.IntegerField()),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Dimensi Tanggal',
                'verbose_name_plural': 'Dimensi Tanggal',
                'db_table': 'dim_date',
                'ordering': ['date_time'],
            },
        ),
        migrations.CreateModel(
            name='DimGender',
            fields=[
                ('gender_id', models.IntegerField(primary_key=True, serialize=False)),
                ('gender', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name_plural': 'Dimensi Gender',
                'db_table': 'dim_gender',
            },
        ),
        migrations.CreateModel(
            name='DimPaymentMethod',
            fields=[
                ('payment_method_id', models.IntegerField(primary_key=True, serialize=False)),
                ('payment_type', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Dimensi Metode Pembayaran',
                'verbose_name_plural': 'Dimensi Metode Pembayaran',
                'db_table': 'dim_payment_method',
                'ordering': ['payment_type'],
            },
        ),
        migrations.CreateModel(
            name='DimProductLine',
            fields=[
                ('product_line_id', models.IntegerField(primary_key=True, serialize=False)),
                ('product_line_name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Dimensi Lini Produk',
                'verbose_name_plural': 'Dimensi Lini Produk',
                'db_table': 'dim_product_line',
                'ordering': ['product_line_name'],
            },
        ),
        migrations.CreateModel(
            name='FactSales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_price', models.FloatField()),
                ('quantity', models.IntegerField()),
                ('cogs', models.FloatField()),
                ('rating', models.FloatField()),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualisasi.dimbranch')),
                ('customer_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualisasi.dimcustomertype')),
                ('date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualisasi.dimdate')),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualisasi.dimpaymentmethod')),
                ('product_line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='visualisasi.dimproductline')),
            ],
            options={
                'verbose_name': 'Fakta Penjualan',
                'verbose_name_plural': 'Fakta Penjualan',
                'db_table': 'fact_sales',
                'ordering': ['-date'],
                'indexes': [models.Index(fields=['date'], name='fact_sales_date_id_5537da_idx'), models.Index(fields=['branch'], name='fact_sales_branch__7c7bd1_idx')],
            },
        ),
        migrations.CreateModel(
            name='FactProductPerform',
            fields=[
                ('product_perform_id', models.AutoField(primary_key=True, serialize=False)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('cogs', models.DecimalField(decimal_places=2, max_digits=10)),
                ('rating', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
                ('branch', models.ForeignKey(db_column='branch_id', on_delete=django.db.models.deletion.DO_NOTHING, to='visualisasi.dimbranch')),
                ('date', models.ForeignKey(db_column='date_id', on_delete=django.db.models.deletion.DO_NOTHING, to='visualisasi.dimdate')),
                ('product_line', models.ForeignKey(db_column='product_line_id', on_delete=django.db.models.deletion.DO_NOTHING, to='visualisasi.dimproductline')),
            ],
            options={
                'verbose_name': 'Fakta Kinerja Produk',
                'verbose_name_plural': 'Fakta Kinerja Produk',
                'db_table': 'fact_product_perform',
                'ordering': ['-date'],
                'indexes': [models.Index(fields=['date'], name='fact_produc_date_id_57f82a_idx'), models.Index(fields=['branch'], name='fact_produc_branch__4eb4b5_idx')],
            },
        ),
        migrations.CreateModel(
            name='FactCustomerBehavior',
            fields=[
                ('customer_behavior_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('cogs', models.DecimalField(decimal_places=2, max_digits=10)),
                ('rating', models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True)),
                ('branch', models.ForeignKey(db_column='branch_id', on_delete=django.db.models.deletion.DO_NOTHING, to='visualisasi.dimbranch')),
                ('customer_type', models.ForeignKey(db_column='customer_type_id', on_delete=django.db.models.deletion.DO_NOTHING, to='visualisasi.dimcustomertype')),
                ('date', models.ForeignKey(db_column='date_id', on_delete=django.db.models.deletion.DO_NOTHING, to='visualisasi.dimdate')),
                ('gender', models.ForeignKey(db_column='gender_id', on_delete=django.db.models.deletion.DO_NOTHING, to='visualisasi.dimgender')),
            ],
            options={
                'verbose_name_plural': 'Fakta Perilaku Pelanggan',
                'db_table': 'fact_customer_behavior',
                'ordering': ['-date'],
                'indexes': [models.Index(fields=['date'], name='fact_custom_date_id_5f3ec9_idx'), models.Index(fields=['customer_type'], name='fact_custom_custome_724934_idx')],
            },
        ),
    ]
