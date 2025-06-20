from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Medicine, Ultrasound, UltrasoundAppointment
import json
from django.utils import timezone

def dashboard(request):
    return render(request, 'pharmacy/home.html')

# Existing views...

from django.shortcuts import render, redirect
from django.urls import reverse

from django.db.models import Max

def ultrasound_appointment(request):
    from django.utils.timezone import now
    pharmacy_name = "AL-Rehmat Clinic"
    doctor_name = "Dr. John Doe"  # You can make this dynamic or configurable

    ultrasounds = Ultrasound.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        number = request.POST.get('number')
        ultrasound_id = request.POST.get('ultrasound')

        try:
            ultrasound = Ultrasound.objects.get(id=ultrasound_id)
        except Ultrasound.DoesNotExist:
            ultrasound = None

        if name and number and ultrasound:
            today = now().date()
            today_appointments = UltrasoundAppointment.objects.filter(date_time__date=today)
            max_token = today_appointments.aggregate(Max('auto_token_number'))['auto_token_number__max']
            if max_token is None:
                max_token = 0
            new_token = max_token + 1

            appointment = UltrasoundAppointment(
                name=name,
                number=number,
                ultrasound=ultrasound,
                price=ultrasound.price,
                date_time=now(),
                auto_token_number=new_token
            )
            appointment.save()
            # Redirect to receipt page with appointment id
            return redirect(reverse('pharmacy:ultrasound_receipt', args=[appointment.id]))

    context = {
        'pharmacy_name': pharmacy_name,
        'doctor_name': doctor_name,
        'ultrasounds': ultrasounds,
    }
    return render(request, 'pharmacy/ultrasound_appointment.html', context)
from django.utils import timezone

def ultrasound_receipt(request, appointment_id):
    pharmacy_name = "AL-Rehmat Clinic And Ultrasound Center"
    doctor_name = "Consultant: Dr.Saba Shabbir"

    try:
        appointment = UltrasoundAppointment.objects.get(id=appointment_id)
    except UltrasoundAppointment.DoesNotExist:
        return redirect(reverse('pharmacy:ultrasound_appointment'))

    # Convert to your PC’s timezone (Asia/Karachi)
    local_dt = timezone.localtime(appointment.date_time)
    formatted_dt = local_dt.strftime('%d-%m-%Y %I:%M %p')

    context = {
        'pharmacy_name': pharmacy_name,
        'doctor_name': doctor_name,
        'appointment': appointment,
        'date_time': formatted_dt,
        'name': appointment.name,
        'number': appointment.number,
        'ultrasound_name': appointment.ultrasound.name,
        'price': appointment.price,
    }
    return render(request, 'pharmacy/ultrasound_receipt.html', context)


from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils.dateparse import parse_date
from .models import UltrasoundAppointment

from .models import UltrasoundAppointmentHistory
from django.utils import timezone

def ultrasound_appointment_history(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Handle deletion with history save
    if request.method == "POST":
        appointment_id = request.POST.get('appointment_id')
        try:
            appointment = UltrasoundAppointment.objects.get(id=appointment_id)
            # Save to history
            UltrasoundAppointmentHistory.objects.create(
                appointment_id=appointment.id,
                auto_token_number=appointment.auto_token_number,
                name=appointment.name,
                number=appointment.number,
                ultrasound_name=appointment.ultrasound.name,
                price=appointment.price,
                date_time=appointment.date_time,
                deleted_at=timezone.now()
            )
            # Delete original appointment
            appointment.delete()
        except UltrasoundAppointment.DoesNotExist:
            pass
        return redirect(request.path_info)

    appointments = UltrasoundAppointment.objects.all().order_by('-date_time')

    if start_date and end_date:
        start = parse_date(start_date)
        end = parse_date(end_date)
        if start and end:
            appointments = appointments.filter(date_time__date__range=(start, end))

    total_profit = appointments.aggregate(total=Sum('price'))['total'] or 0

    context = {
        'appointments': appointments,
        'total_profit': total_profit,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'pharmacy/ultrasound_appointment_history.html', context)


def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'pharmacy/medicine_list.html', {'medicines': medicines})

def sales(request):
    return render(request, 'pharmacy/sales.html')

def search_medicines(request):
    query = request.GET.get('q', '')
    medicines = []
    if query:
        medicines = list(Medicine.objects.filter(name__istartswith=query).values('id', 'name', 'sale_price', 'stock'))
    return JsonResponse(medicines, safe=False)

from .models import Sale, SaleItem
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from .models import Sale, SaleItem, Medicine # adjust the import if needed

from django.db import transaction
from django.http import JsonResponse
import json
from .models import Sale, SaleItem, Medicine

def receipt(request):
    if request.method == 'POST':
        import traceback
        data = json.loads(request.body)
        user_info = data.get('user_info', {})
        cart = data.get('cart', [])
        total_price = sum(item['price'] * item['quantity'] for item in cart)
        discount = user_info.get('discount', 0)  # get discount percentage

        try:
            with transaction.atomic():
                # Create Sale
                age_value = user_info.get('age', None)
                if age_value == '' or age_value is None:
                    age_value = None
                else:
                    try:
                        age_value = int(age_value)
                    except ValueError:
                        age_value = None

                sale = Sale.objects.create(
                    customer_name=user_info.get('name', ''),
                    customer_age=age_value,
                    customer_number=user_info.get('number', ''),
                    total_price=total_price,
                    discount=discount
                )

                for item in cart:
                    # Create SaleItem
                    SaleItem.objects.create(
                        sale=sale,
                        medicine_name=item['name'],
                        quantity=item['quantity'],
                        price=item['price']
                    )

                    # Deduct from stock
                    try:
                        medicine = Medicine.objects.get(name=item['name'])

                        if medicine.stock >= item['quantity']:
                            medicine.stock -= item['quantity']
                            medicine.save()
                        else:
                            return JsonResponse({'error': f"Not enough stock for {item['name']}. Available: {medicine.stock}"}, status=400)

                    except Medicine.DoesNotExist:
                        return JsonResponse({'error': f"Medicine '{item['name']}' not found."}, status=400)

            return JsonResponse({'sale_id': sale.id})

        except Exception as e:
            tb = traceback.format_exc()
            print("Exception in receipt POST:", tb)
            return JsonResponse({'error': str(e), 'traceback': tb}, status=500)

    # GET request
    sale_id = request.GET.get('sale_id')
    if sale_id:
        try:
            sale = Sale.objects.get(id=sale_id)
            sale_items = SaleItem.objects.filter(sale=sale)
            total_price = sale.total_price
            user_info = {
                'name': sale.customer_name,
                'age': sale.customer_age,
                'number': sale.customer_number,
                'discount': sale.discount
            }
            context = {
                'pharmacy_name': 'AL Rehmat Clinic',
                'user_info': user_info,
                'cart': [{'name': item.medicine_name, 'quantity': item.quantity, 'price': item.price} for item in sale_items],
                'total_price': total_price,
                'sale_id': sale.id,
                'discount': sale.discount
            }
            return render(request, 'pharmacy/receipt.html', context)
        except Sale.DoesNotExist:
            return redirect('pharmacy:sales')

    return render(request, 'pharmacy/receipt.html', {
        'pharmacy_name': 'Al-Rehmat Clinic',
        'cart': [],
        'total_price': 0,
        'discount': 0
    })





from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch
from datetime import datetime
import json
from django.shortcuts import render
from django.db.models import Prefetch
from datetime import datetime
from .models import Sale, SaleItem, Medicine

# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch
from datetime import datetime
import json

from .models import Sale, SaleItem, Medicine
from decimal import Decimal

def sales_history(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    sales_qs = Sale.objects.prefetch_related(
        Prefetch('items', queryset=SaleItem.objects.all())
    ).order_by('-date_time')  # Order latest to oldest by date_time descending

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            sales_qs = sales_qs.filter(date_time__date__range=(start, end))
        except ValueError:
            pass

    sales = list(sales_qs)
    total_profit = Decimal('0.0')
    medicine_prices = {med.name: med.original_price for med in Medicine.objects.all()}

    for sale in sales:
        discount_percent = Decimal(sale.discount or 0)
        total_sale_price = sum(item.price * item.quantity for item in sale.items.all())
        for item in sale.items.all():
            original_price = medicine_prices.get(item.medicine_name, Decimal('0.0'))
            item.original_price = original_price
            # Calculate item's price proportion of total sale price
            item_price_total = item.price * item.quantity
            if total_sale_price > 0:
                item_discount = (item_price_total / total_sale_price) * discount_percent
            else:
                item_discount = Decimal('0.0')
            # Adjusted price after discount
            adjusted_price = item.price * (Decimal('1.0') - item_discount / Decimal('100.0'))
            item.profit = (adjusted_price - original_price) * item.quantity
            total_profit += item.profit

    return render(request, 'pharmacy/sales_history.html', {
        'sales': sales,
        'total_profit': total_profit,
    })

@csrf_exempt
@csrf_exempt
def update_sale_quantity(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sale_id = data.get('sale_id')
            medicine_name = data.get('medicine_name')
            quantity = int(data.get('quantity'))

            sale_item = SaleItem.objects.get(sale_id=sale_id, medicine_name=medicine_name)
            sale_item.quantity = quantity
            sale_item.save()

            # Get original price
            try:
                medicine = Medicine.objects.get(name=medicine_name)
                original_price = medicine.original_price
            except Medicine.DoesNotExist:
                original_price = 0

            new_profit = (sale_item.price - original_price) * quantity

            # Calculate total profit
            total_profit = 0
            all_items = SaleItem.objects.select_related('sale')
            medicine_prices = {m.name: m.original_price for m in Medicine.objects.all()}

            for item in all_items:
                orig_price = medicine_prices.get(item.medicine_name, 0)
                total_profit += (item.price - orig_price) * item.quantity

            return JsonResponse({
                'success': True,
                'new_profit': new_profit,
                'total_profit': total_profit
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .models import Medicine, ReturnLog

@csrf_protect
def return_medicine(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            medicine_name = data.get('medicine_name')
            quantity = int(data.get('quantity', 0))
            reason = data.get('reason', '')

            medicine = Medicine.objects.get(name=medicine_name)
            medicine.stock += quantity
            medicine.save()

            ReturnLog.objects.create(medicine=medicine, quantity=quantity, reason=reason)

            return JsonResponse({'success': True, 'message': f"{quantity} units of {medicine_name} returned."})

        except Medicine.DoesNotExist:
            return JsonResponse({'error': f"Medicine '{medicine_name}' not found."}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'pharmacy/return_form.html')
