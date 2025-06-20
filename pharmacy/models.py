from django.db import models
from django.utils import timezone
import uuid

class Medicine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    stock = models.IntegerField(default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Sale(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_age = models.IntegerField(null=True, blank=True)
    customer_number = models.CharField(max_length=20, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # discount percentage
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale {self.id} - {self.customer_name}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.medicine_name} ({self.quantity})"

class ReturnLog(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Return {self.id} - {self.medicine.name}"

class Ultrasound(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class UltrasoundAppointment(models.Model):
    auto_token_number = models.IntegerField(null=True, blank=True, editable=False)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=20)
    ultrasound = models.ForeignKey(Ultrasound, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_time = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Remove token_number generation logic
        # Set price from ultrasound if not set or changed
        if not self.price or self.price != self.ultrasound.price:
            self.price = self.ultrasound.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.auto_token_number} - {self.name}"

class UltrasoundAppointmentHistory(models.Model):
    appointment_id = models.IntegerField()
    auto_token_number = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=20)
    ultrasound_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_time = models.DateTimeField()
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History {self.appointment_id} - {self.name}"
