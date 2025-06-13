# visualisasi/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL '' akan memanggil dashboard_view
    path('', views.dashboard_view, name='dashboard'),
]