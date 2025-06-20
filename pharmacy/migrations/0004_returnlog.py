# Generated by Django 4.2.10 on 2025-06-01 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0003_sale_saleitem_delete_salehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReturnLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('reason', models.TextField(blank=True)),
                ('date_returned', models.DateTimeField(auto_now_add=True)),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pharmacy.medicine')),
            ],
        ),
    ]
