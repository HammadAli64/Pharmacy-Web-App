from django.contrib import admin
from .models import Medicine, Ultrasound, UltrasoundAppointment
from .models import Sale, SaleItem, ReturnLog,UltrasoundAppointmentHistory


admin.site.register(Ultrasound)
admin.site.register(UltrasoundAppointment)
admin.site.register(UltrasoundAppointmentHistory)
    


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name',  'stock', 'sale_price', 'original_price')
    search_fields = ('name',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'total_price', 'date_time')
    search_fields = ('customer_name',)
    list_filter = ('date_time',)
@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'medicine_name', 'quantity', 'price')

@admin.register(ReturnLog)
class ReturnLogAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'quantity',  'reason')