# Generated by Django 4.2.10 on 2025-06-14 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0008_ultrasoundappointmenthistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
