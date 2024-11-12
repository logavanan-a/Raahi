# Generated by Django 4.2.1 on 2023-06-21 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0010_remove_orderrequest_partner_remove_orderrequest_uuid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrequest',
            name='order_status',
            field=models.IntegerField(blank=True, choices=[(1, 'Pending'), (2, 'Submit for Approval'), (3, 'Approved'), (4, 'Rejected')], null=True),
        ),
    ]
