# Generated by Django 4.2.10 on 2025-06-03 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0007_remove_ultrasoundappointment_token_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='UltrasoundAppointmentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.IntegerField()),
                ('auto_token_number', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('number', models.CharField(max_length=20)),
                ('ultrasound_name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_time', models.DateTimeField()),
                ('deleted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
