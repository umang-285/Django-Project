# Generated by Django 4.1.6 on 2023-06-01 10:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0003_carimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='car',
            name='image',
        ),
    ]
