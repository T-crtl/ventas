# Generated by Django 5.1.4 on 2025-06-17 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulo_ventas', '0043_backorder_comentarios_factura_comentarios'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='factura',
            name='cve_doc',
        ),
        migrations.RemoveField(
            model_name='factura',
            name='doc_sig',
        ),
        migrations.AlterField(
            model_name='factura',
            name='factura',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='factura',
            name='folio',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
