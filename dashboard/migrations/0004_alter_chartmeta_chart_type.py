# Generated by Django 4.2.1 on 2024-02-03 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_alter_chartmeta_chart_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chartmeta',
            name='chart_type',
            field=models.IntegerField(blank=True, choices=[(1, 'Column Chart'), (2, 'Pie Chart'), (3, 'Table Chart'), (4, 'Bar Chart'), (5, 'Column Stack'), (6, 'Bar Dynamic Chart'), (7, 'Column Dynamic Stack'), (8, 'Card chart'), (9, 'Geo chart'), (10, 'Line chart'), (11, 'Progressive Line'), (12, 'Dounut chart')], help_text='1=Column Chart, 2=Pie Chart, 3=Table Chart, 4=Bar Chart, 5=Column Stack, 6=Bar Dynamic Chart, 7=Column Dynamic Stack, 8=Card Chart', null=True),
        ),
    ]
