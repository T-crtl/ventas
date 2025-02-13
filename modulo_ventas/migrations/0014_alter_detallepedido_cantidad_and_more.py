# Generated by Django 5.1.4 on 2025-01-15 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulo_ventas', '0013_remove_pedido_productos_detallepedido'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detallepedido',
            name='cantidad',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='nombre_contacto',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
