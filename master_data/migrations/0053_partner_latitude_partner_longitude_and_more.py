# Generated by Django 4.2.1 on 2024-01-18 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0052_alter_userdonorlinkage_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='latitude',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='longitude',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='visioncenter',
            name='latitude',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='visioncenter',
            name='longitude',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
