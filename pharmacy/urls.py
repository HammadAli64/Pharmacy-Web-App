from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('medicines', views.medicine_list, name='medicine_list'),
    path('sales/', views.sales, name='sales'),
    path('search/', views.search_medicines, name='search_medicines'),
    path('receipt/', views.receipt, name='receipt'),
    path('sales_history/', views.sales_history, name='sales_history'),
    path('', views.dashboard, name='dashboard'),
    path('return/', views.return_medicine, name='return_medicine'),
    path('update-sale-quantity/', views.update_sale_quantity, name='update_sale_quantity'),
    path('ultrasound-appointment/', views.ultrasound_appointment, name='ultrasound_appointment'),
    path('ultrasound-receipt/<int:appointment_id>/', views.ultrasound_receipt, name='ultrasound_receipt'),
    path('ultrasound-appointment-history/', views.ultrasound_appointment_history, name='ultrasound_appointment_history'),
]
