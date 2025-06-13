from django.db import models

# --- Tabel Dimensi ---

class DimDate(models.Model):
    date_id = models.IntegerField(primary_key=True)
    date_time = models.DateTimeField(db_column='date_time')
    full_date = models.DateField(unique=True)
    day = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        db_table = 'dim_date'
        ordering = ['date_time']
        verbose_name = 'Dimensi Tanggal'
        verbose_name_plural = 'Dimensi Tanggal'

    def __str__(self):
        return str(self.full_date)


class DimProductLine(models.Model):
    product_line_id = models.IntegerField(primary_key=True)
    product_line_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'dim_product_line'
        ordering = ['product_line_name']
        verbose_name = 'Dimensi Lini Produk'
        verbose_name_plural = 'Dimensi Lini Produk'

    def __str__(self):
        return self.product_line_name


class DimBranch(models.Model):
    branch_id = models.IntegerField(primary_key=True)
    branch_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    class Meta:
        db_table = 'dim_branch'
        ordering = ['branch_name']
        verbose_name = 'Dimensi Cabang'
        verbose_name_plural = 'Dimensi Cabang'

    def __str__(self):
        return f"{self.branch_name} ({self.city})"


class DimPaymentMethod(models.Model):
    payment_method_id = models.IntegerField(primary_key=True)
    payment_type = models.CharField(max_length=255)

    class Meta:
        db_table = 'dim_payment_method'
        ordering = ['payment_type']
        verbose_name = 'Dimensi Metode Pembayaran'
        verbose_name_plural = 'Dimensi Metode Pembayaran'

    def __str__(self):
        return self.payment_type


class DimCustomerType(models.Model):
    customer_type_id = models.IntegerField(primary_key=True)
    customer_type = models.CharField(max_length=255)

    class Meta:
        db_table = 'dim_customer_type'
        ordering = ['customer_type']
        verbose_name = 'Dimensi Tipe Pelanggan'
        verbose_name_plural = 'Dimensi Tipe Pelanggan'

    def __str__(self):
        return self.customer_type


class DimGender(models.Model):
    gender_id = models.IntegerField(primary_key=True)
    gender = models.CharField(max_length=10)

    class Meta:
        db_table = 'dim_gender'
        verbose_name_plural = 'Dimensi Gender'

    def __str__(self):
        return self.gender

# --- Tabel Fakta ---

class FactSales(models.Model):
    date = models.ForeignKey(DimDate, on_delete=models.CASCADE)
    branch = models.ForeignKey(DimBranch, on_delete=models.CASCADE)
    product_line = models.ForeignKey(DimProductLine, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(DimPaymentMethod, on_delete=models.CASCADE)
    customer_type = models.ForeignKey(DimCustomerType, on_delete=models.CASCADE)
    unit_price = models.FloatField()
    quantity = models.IntegerField()
    cogs = models.FloatField()
    rating = models.FloatField()


    class Meta:
        db_table = 'fact_sales'
        verbose_name = 'Fakta Penjualan'
        verbose_name_plural = 'Fakta Penjualan'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['branch']),
        ]

    def __str__(self):
        return f"Sales ID: {self.sales_id} | Date: {self.date.full_date}"


class FactProductPerform(models.Model):
    product_perform_id = models.AutoField(primary_key=True)

    product_line = models.ForeignKey(DimProductLine, on_delete=models.DO_NOTHING, db_column='product_line_id')
    branch = models.ForeignKey(DimBranch, on_delete=models.DO_NOTHING, db_column='branch_id')
    date = models.ForeignKey(DimDate, on_delete=models.DO_NOTHING, db_column='date_id')

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    cogs = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    class Meta:
        db_table = 'fact_product_perform'
        verbose_name = 'Fakta Kinerja Produk'
        verbose_name_plural = 'Fakta Kinerja Produk'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['branch']),
        ]

    def __str__(self):
        return f"ProductPerf ID: {self.product_perform_id} | Date: {self.date.full_date}"


class FactCustomerBehavior(models.Model):
    customer_behavior_id = models.AutoField(primary_key=True)

    date = models.ForeignKey(DimDate, on_delete=models.DO_NOTHING, db_column='date_id')
    customer_type = models.ForeignKey(DimCustomerType, on_delete=models.DO_NOTHING, db_column='customer_type_id')
    gender = models.ForeignKey(DimGender, on_delete=models.DO_NOTHING, db_column='gender_id')
    branch = models.ForeignKey(DimBranch, on_delete=models.DO_NOTHING, db_column='branch_id')

    quantity = models.IntegerField()
    cogs = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    class Meta:
        db_table = 'fact_customer_behavior'
        verbose_name_plural = 'Fakta Perilaku Pelanggan'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['customer_type']),
        ]

    def __str__(self):
        return f"CustomerBehavior ID: {self.customer_behavior_id} | Date: {self.date.full_date}"
