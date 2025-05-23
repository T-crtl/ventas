# Generated by Django 5.1.4 on 2025-04-16 23:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulo_ventas', '0038_remove_backorder_factura_relacionada_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='backorder',
            name='creado_por',
        ),
        migrations.RemoveField(
            model_name='backorder',
            name='folio_original',
        ),
        migrations.RemoveField(
            model_name='productobackorder',
            name='backorder',
        ),
        migrations.RemoveField(
            model_name='productobackorder',
            name='cantidad_pendiente',
        ),
        migrations.RemoveField(
            model_name='productobackorder',
            name='fecha_surtido',
        ),
        migrations.RemoveField(
            model_name='productobackorder',
            name='lote_asignado',
        ),
        migrations.RemoveField(
            model_name='productobackorder',
            name='producto',
        ),
        migrations.AddField(
            model_name='backorder',
            name='folio',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productobackorder',
            name='cantidad',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productobackorder',
            name='descripcion',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productobackorder',
            name='factura',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='productos_backorder', to='modulo_ventas.factura'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productobackorder',
            name='lote',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='backorder',
            name='cliente_clave',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='backorder',
            name='cliente_nombre',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='backorder',
            name='rfc',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productobackorder',
            name='cantidad_real',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='productobackorder',
            name='codigo',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
