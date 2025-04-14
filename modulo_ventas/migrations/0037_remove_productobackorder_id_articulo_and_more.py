# Generated by Django 5.1.4 on 2025-04-14 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulo_ventas', '0036_backorder_productobackorder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productobackorder',
            name='id_articulo',
        ),
        migrations.RemoveField(
            model_name='productobackorder',
            name='nombre_articulo',
        ),
        migrations.AddField(
            model_name='productobackorder',
            name='codigo',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='productobackorder',
            name='producto',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='productobackorder',
            name='cantidad_pendiente',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
