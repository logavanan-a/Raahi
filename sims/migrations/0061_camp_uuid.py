# Generated by Django 4.2.1 on 2023-09-27 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0060_orderrequest_courier_name_orderrequest_invoice_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='camp',
            name='uuid',
            field=models.CharField(blank=True, db_index=True, max_length=150, null=True, unique=True),
        ),
    ]
