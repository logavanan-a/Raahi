# Generated by Django 4.2.1 on 2023-07-24 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0024_district_sync_status_donor_sync_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donorpartnerlinkage',
            name='donor',
            field=models.ManyToManyField(blank=True, related_name='donor_partner', to='master_data.donor'),
        ),
    ]
