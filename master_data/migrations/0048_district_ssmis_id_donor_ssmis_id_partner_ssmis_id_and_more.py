# Generated by Django 4.2.1 on 2023-12-15 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0047_visioncenter_donor'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='ssmis_id',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='donor',
            name='ssmis_id',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='ssmis_id',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='state',
            name='ssmis_id',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='ssmis_id',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='visioncenter',
            name='ssmis_id',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='zone',
            name='ssmis_id',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
