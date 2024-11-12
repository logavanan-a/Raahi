# Generated by Django 4.2.1 on 2024-01-25 09:58

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('master_data', '0053_partner_latitude_partner_longitude_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VersionUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveIntegerField(choices=[(1, 'Inactive'), (2, 'Active'), (3, 'Pending'), (4, 'Approved'), (5, 'Rejected')], db_index=True, default=2)),
                ('server_created_on', models.DateTimeField(auto_now_add=True)),
                ('server_modified_on', models.DateTimeField(auto_now=True)),
                ('sync_status', models.PositiveIntegerField(default=2)),
                ('version_code', models.IntegerField(default=0)),
                ('version_name', models.CharField(blank=True, max_length=100, null=True)),
                ('force_update', models.BooleanField(default=False)),
                ('interface', models.PositiveIntegerField(choices=[(1, 'Db'), (2, 'Web'), (3, 'App')], default=3)),
                ('releasenotes', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('release_date', models.DateField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='created%(app_label)s_%(class)s_related', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='modified%(app_label)s_%(class)s_related', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
