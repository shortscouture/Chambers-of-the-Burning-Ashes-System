# Generated by Django 5.1.2 on 2025-02-22 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('parish_staff', 'Parish Staff'), ('customer', 'Customer'), ('admin', 'Admin')], default='customer', max_length=20),
        ),
    ]
