# Generated by Django 4.0.6 on 2024-12-08 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remauto_crm_system', '0007_alter_orderstatus_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='vehicle_info',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]