# Generated by Django 5.1.4 on 2025-02-13 19:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modulo_ventas', '0029_area_directorio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='directorio',
            name='publico',
        ),
    ]
