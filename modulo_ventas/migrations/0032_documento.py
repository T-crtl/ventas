# Generated by Django 5.1.4 on 2025-03-12 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('modulo_ventas', '0031_remove_area_nombre_directorio_publico_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('archivo', models.FileField(upload_to='documentos/')),
                ('fecha_subida', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
