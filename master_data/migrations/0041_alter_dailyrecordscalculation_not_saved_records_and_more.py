# Generated by Django 4.2.1 on 2023-10-11 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0040_dailyrecordscalculation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyrecordscalculation',
            name='not_saved_records',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='dailyrecordscalculation',
            name='record',
            field=models.CharField(max_length=1500),
        ),
        migrations.AlterField(
            model_name='dailyrecordscalculation',
            name='saved_records',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
