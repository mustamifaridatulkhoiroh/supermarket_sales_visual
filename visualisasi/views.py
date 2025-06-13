from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Avg
import json
from collections import defaultdict

from .models import (
    FactSales, DimDate, DimProductLine, DimBranch, DimPaymentMethod, DimCustomerType,
    FactProductPerform, DimGender, FactCustomerBehavior
)

def dashboard_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    fact_schema_filter = request.GET.get('fact_schema', '').strip()

    total_sales_expr_sales = ExpressionWrapper(F('unit_price') * F('quantity'), output_field=DecimalField(max_digits=12, decimal_places=2))
    gross_profit_expr_sales = ExpressionWrapper((F('unit_price') * F('quantity')) - F('cogs'), output_field=DecimalField(max_digits=12, decimal_places=2))

    sales_queryset = FactSales.objects.none()
    product_perform_queryset = FactProductPerform.objects.none()
    customer_behavior_queryset = FactCustomerBehavior.objects.none()

    if not fact_schema_filter or fact_schema_filter == 'FactSales':
        sales_queryset = FactSales.objects.all()
    if not fact_schema_filter or fact_schema_filter == 'FactProductPerform':
        product_perform_queryset = FactProductPerform.objects.all()
    if not fact_schema_filter or fact_schema_filter == 'FactCustomerBehavior':
        customer_behavior_queryset = FactCustomerBehavior.objects.all()

    if start_date:
        if sales_queryset.exists():
            sales_queryset = sales_queryset.filter(date__full_date__gte=start_date)
        if product_perform_queryset.exists():
            product_perform_queryset = product_perform_queryset.filter(date__full_date__gte=start_date)
        if customer_behavior_queryset.exists():
            customer_behavior_queryset = customer_behavior_queryset.filter(date__full_date__gte=start_date)
    if end_date:
        if sales_queryset.exists():
            sales_queryset = sales_queryset.filter(date__full_date__lte=end_date)
        if product_perform_queryset.exists():
            product_perform_queryset = product_perform_queryset.filter(date__full_date__lte=end_date)
        if customer_behavior_queryset.exists():
            customer_behavior_queryset = customer_behavior_queryset.filter(date__full_date__lte=end_date)

    # --- Faktual Sales ---

    labels_sales_by_date = []
    data_total_sales = []
    data_total_quantity = []
    data_gross_profit = []
    data_cogs_sales = []

    labels_product_line_sales = []
    data_product_line_sales = []
    labels_gross_profit_product_line = []
    data_gross_profit_product_line = []

    labels_branch_sales = []
    data_branch_sales = []
    labels_quantity_branch_sales = []
    data_quantity_branch_sales = []

    labels_payment_sales = []
    data_payment_sales = []

    payment_method_trend_data = defaultdict(dict)
    unit_price_trend_data = defaultdict(dict)

    if sales_queryset.exists():
        # Penjualan per tanggal
        sales_by_date = sales_queryset.values('date__full_date').annotate(total_sales=Sum(total_sales_expr_sales)).order_by('date__full_date')
        labels_sales_by_date = [item['date__full_date'].strftime('%Y-%m-%d') for item in sales_by_date]
        data_total_sales = [float(item['total_sales']) for item in sales_by_date]

        quantity_by_date = sales_queryset.values('date__full_date').annotate(total_quantity=Sum('quantity')).order_by('date__full_date')
        data_total_quantity = [float(item['total_quantity']) for item in quantity_by_date]

        gross_profit_by_date = sales_queryset.values('date__full_date').annotate(total_gross_profit=Sum(gross_profit_expr_sales)).order_by('date__full_date')
        data_gross_profit = [float(item['total_gross_profit']) for item in gross_profit_by_date]

        cogs_by_date_sales = sales_queryset.values('date__full_date').annotate(total_cogs=Sum('cogs')).order_by('date__full_date')
        data_cogs_sales = [float(item['total_cogs']) for item in cogs_by_date_sales]

        # Penjualan per lini produk
        sales_by_product_line = sales_queryset.values('product_line__product_line_name').annotate(total_sales=Sum(total_sales_expr_sales)).order_by('-total_sales')
        labels_product_line_sales = [item['product_line__product_line_name'] for item in sales_by_product_line]
        data_product_line_sales = [float(item['total_sales']) for item in sales_by_product_line]

        gross_profit_by_product_line = sales_queryset.values('product_line__product_line_name').annotate(total_gross_profit=Sum(gross_profit_expr_sales)).order_by('-total_gross_profit')
        labels_gross_profit_product_line = [item['product_line__product_line_name'] for item in gross_profit_by_product_line]
        data_gross_profit_product_line = [float(item['total_gross_profit']) for item in gross_profit_by_product_line]

        # Penjualan per cabang
        sales_by_branch = sales_queryset.values('branch__branch_name', 'branch__city').annotate(total_sales=Sum(total_sales_expr_sales)).order_by('-total_sales')
        labels_branch_sales = [f"{item['branch__branch_name']} ({item['branch__city']})" for item in sales_by_branch]
        data_branch_sales = [float(item['total_sales']) for item in sales_by_branch]

        quantity_by_branch_sales = sales_queryset.values('branch__branch_name', 'branch__city').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
        labels_quantity_branch_sales = [f"{item['branch__branch_name']} ({item['branch__city']})" for item in quantity_by_branch_sales]
        data_quantity_branch_sales = [float(item['total_quantity']) for item in quantity_by_branch_sales]

        # Metode pembayaran
        sales_by_payment_method = sales_queryset.values('payment_method__payment_type').annotate(total_sales=Sum(total_sales_expr_sales)).order_by('-total_sales')
        labels_payment_sales = [item['payment_method__payment_type'] for item in sales_by_payment_method]
        data_payment_sales = [float(item['total_sales']) for item in sales_by_payment_method]

        sales_trend_by_payment_method = sales_queryset.values('date__full_date', 'payment_method__payment_type').annotate(total_sales=Sum(total_sales_expr_sales)).order_by('date__full_date')
        for item in sales_trend_by_payment_method:
            date_str = item['date__full_date'].strftime('%Y-%m-%d')
            payment_method_trend_data[date_str][item['payment_method__payment_type']] = float(item['total_sales'])

        avg_unit_price_by_product_line_date = sales_queryset.values('date__full_date', 'product_line__product_line_name').annotate(avg_price=Avg('unit_price')).order_by('date__full_date')
        for item in avg_unit_price_by_product_line_date:
            date_str = item['date__full_date'].strftime('%Y-%m-%d')
            unit_price_trend_data[date_str][item['product_line__product_line_name']] = float(item['avg_price'])

    # --- Faktual Product Performance ---

    labels_prod_perf_product_line = []
    data_avg_rating_prod_perf = []
    labels_prod_perf_branch = []
    data_avg_rating_branch_pp = []
    labels_quantity_prod_perform_product_line = []
    data_quantity_prod_perform_product_line = []
    labels_cogs_prod_perform_product_line = []
    data_cogs_prod_perform_product_line = []

    if product_perform_queryset.exists():
        avg_rating_by_product_line_pp = product_perform_queryset.values('product_line__product_line_name').annotate(avg_rating=Avg('rating')).order_by('-avg_rating')
        labels_prod_perf_product_line = [item['product_line__product_line_name'] for item in avg_rating_by_product_line_pp]
        data_avg_rating_prod_perf = [float(item['avg_rating']) for item in avg_rating_by_product_line_pp]

        avg_rating_by_branch_pp = product_perform_queryset.values('branch__branch_name', 'branch__city').annotate(avg_rating=Avg('rating')).order_by('-avg_rating')
        labels_prod_perf_branch = [f"{item['branch__branch_name']} ({item['branch__city']})" for item in avg_rating_by_branch_pp]
        data_avg_rating_branch_pp = [float(item['avg_rating']) for item in avg_rating_by_branch_pp]

        quantity_prod_perform_by_product_line = product_perform_queryset.values('product_line__product_line_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
        labels_quantity_prod_perform_product_line = [item['product_line__product_line_name'] for item in quantity_prod_perform_by_product_line]
        data_quantity_prod_perform_product_line = [float(item['total_quantity']) for item in quantity_prod_perform_by_product_line]

        cogs_prod_perform_by_product_line = product_perform_queryset.values('product_line__product_line_name').annotate(total_cogs=Sum('cogs')).order_by('-total_cogs')
        labels_cogs_prod_perform_product_line = [item['product_line__product_line_name'] for item in cogs_prod_perform_by_product_line]
        data_cogs_prod_perform_product_line = [float(item['total_cogs']) for item in cogs_prod_perform_by_product_line]

    # --- Faktual Customer Behavior ---

    labels_customer_type_behavior = []
    data_customer_type_quantity = []
    data_customer_type_avg_rating = []
    labels_cogs_cust_behavior_customer_type = []
    data_cogs_cust_behavior_customer_type = []
    labels_gender_quantity = []
    data_gender_quantity = []
    labels_gender_rating = []
    data_avg_rating_gender = []
    branch_customer_type_quantity_data = defaultdict(dict)

    if customer_behavior_queryset.exists():
        customer_type_behavior = customer_behavior_queryset.values('customer_type__customer_type').annotate(total_quantity=Sum('quantity'), avg_rating=Avg('rating')).order_by('-total_quantity')
        labels_customer_type_behavior = [item['customer_type__customer_type'] for item in customer_type_behavior]
        data_customer_type_quantity = [float(item['total_quantity']) for item in customer_type_behavior]
        data_customer_type_avg_rating = [float(item['avg_rating']) for item in customer_type_behavior]

        cogs_cust_behavior_by_customer_type = customer_behavior_queryset.values('customer_type__customer_type').annotate(total_cogs=Sum('cogs')).order_by('-total_cogs')
        labels_cogs_cust_behavior_customer_type = [item['customer_type__customer_type'] for item in cogs_cust_behavior_by_customer_type]
        data_cogs_cust_behavior_customer_type = [float(item['total_cogs']) for item in cogs_cust_behavior_by_customer_type]

        quantity_by_gender = customer_behavior_queryset.values('gender__gender').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
        labels_gender_quantity = [item['gender__gender'] for item in quantity_by_gender]
        data_gender_quantity = [float(item['total_quantity']) for item in quantity_by_gender]

        avg_rating_by_gender = customer_behavior_queryset.values('gender__gender').annotate(avg_rating=Avg('rating')).order_by('-avg_rating')
        labels_gender_rating = [item['gender__gender'] for item in avg_rating_by_gender]
        data_avg_rating_gender = [float(item['avg_rating']) for item in avg_rating_by_gender]

        quantity_by_branch_customer_type = customer_behavior_queryset.values('branch__branch_name', 'branch__city', 'customer_type__customer_type').annotate(total_quantity=Sum('quantity')).order_by('branch__branch_name')
        for item in quantity_by_branch_customer_type:
            branch_label = f"{item['branch__branch_name']} ({item['branch__city']})"
            cust_type = item['customer_type__customer_type']
            branch_customer_type_quantity_data[branch_label][cust_type] = float(item['total_quantity'])

    all_branches_data = DimBranch.objects.all().order_by('branch_name')
    all_product_lines_data = DimProductLine.objects.all().order_by('product_line_name')
    all_fact_schemas = ['FactSales', 'FactProductPerform', 'FactCustomerBehavior']

    context = {
        'labels_sales_by_date': json.dumps(labels_sales_by_date),
        'data_total_sales': json.dumps(data_total_sales),
        'data_total_quantity': json.dumps(data_total_quantity),
        'data_gross_profit': json.dumps(data_gross_profit),
        'data_cogs_sales': json.dumps(data_cogs_sales),
        'labels_product_line_sales': json.dumps(labels_product_line_sales),
        'data_product_line_sales': json.dumps(data_product_line_sales),
        'labels_gross_profit_product_line': json.dumps(labels_gross_profit_product_line),
        'data_gross_profit_product_line': json.dumps(data_gross_profit_product_line),
        'labels_branch_sales': json.dumps(labels_branch_sales),
        'data_branch_sales': json.dumps(data_branch_sales),
        'labels_quantity_branch_sales': json.dumps(labels_quantity_branch_sales),
        'data_quantity_branch_sales': json.dumps(data_quantity_branch_sales),
        'labels_payment_sales': json.dumps(labels_payment_sales),
        'data_payment_sales': json.dumps(data_payment_sales),
        'payment_method_trend_data': json.dumps(payment_method_trend_data),
        'unit_price_trend_data': json.dumps(unit_price_trend_data),
        'labels_prod_perf_product_line': json.dumps(labels_prod_perf_product_line),
        'data_avg_rating_prod_perf': json.dumps(data_avg_rating_prod_perf),
        'labels_prod_perf_branch': json.dumps(labels_prod_perf_branch),
        'data_avg_rating_branch_pp': json.dumps(data_avg_rating_branch_pp),
        'labels_quantity_prod_perform_product_line': json.dumps(labels_quantity_prod_perform_product_line),
        'data_quantity_prod_perform_product_line': json.dumps(data_quantity_prod_perform_product_line),
        'labels_cogs_prod_perform_product_line': json.dumps(labels_cogs_prod_perform_product_line),
        'data_cogs_prod_perform_product_line': json.dumps(data_cogs_prod_perform_product_line),
        'labels_customer_type_behavior': json.dumps(labels_customer_type_behavior),
        'data_customer_type_quantity': json.dumps(data_customer_type_quantity),
        'data_customer_type_avg_rating': json.dumps(data_customer_type_avg_rating),
        'labels_cogs_cust_behavior_customer_type': json.dumps(labels_cogs_cust_behavior_customer_type),
        'data_cogs_cust_behavior_customer_type': json.dumps(data_cogs_cust_behavior_customer_type),
        'labels_gender_quantity': json.dumps(labels_gender_quantity),
        'data_gender_quantity': json.dumps(data_gender_quantity),
        'labels_gender_rating': json.dumps(labels_gender_rating),
        'data_avg_rating_gender': json.dumps(data_avg_rating_gender),
        'branch_customer_type_quantity_data': json.dumps(branch_customer_type_quantity_data),
        'all_branches_data': all_branches_data,
        'all_product_lines_data': all_product_lines_data,
        'all_fact_schemas': all_fact_schemas,
        'selected_fact_schema': fact_schema_filter,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'visualisasi/dashboard.html', context)
