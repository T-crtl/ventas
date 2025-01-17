from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Pedido(models.Model):
    ESTATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('enviado', 'Enviado'),
    ]

    nombre_cliente = models.CharField(max_length=255)
    numero_cliente = models.IntegerField(default=0)
    nombre_contacto = models.CharField(max_length=255, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    calle = models.CharField(max_length=255)
    numero = models.CharField(max_length=50)
    colonia = models.CharField(max_length=255)
    municipio = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)
    codigo_postal = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    lista_items = models.IntegerField(choices=[(i, str(i)) for i in range(1, 4)], default=1)
    estatus = models.CharField(
        max_length=20,
        choices=ESTATUS_CHOICES,
        default='pendiente'
    )
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Pedido {self.nombre_cliente} - {self.estatus}"
    
class Producto(models.Model):
    LINEA_CHOICES = [
        ('inbelleza', 'Inbelleza'),
        ('barber', 'Barber'),
        ('platinum', 'Platinum'),
        ('none', 'None')
    ]
    
    nombre_producto = models.CharField(max_length=255)
    qty_caja = models.IntegerField(default=0)
    linea = models.CharField(
        max_length=20,
        choices=LINEA_CHOICES,
        default='none'
    )
    precio_1 = models.FloatField(default=0)
    precio_2 = models.FloatField(default=0)
    precio_3 = models.FloatField(default=0)
    imagen = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.nombre_producto
    
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def calcular_subtotal(self):
        # Obtener el precio basado en la selección del pedido
        if self.pedido.lista_items == 1:
            precio = self.producto.precio_1
        elif self.pedido.lista_items == 2:
            precio = self.producto.precio_2
        elif self.pedido.lista_items == 3:
            precio = self.producto.precio_3
        else:
            precio = 0
        return self.cantidad * precio

    def __str__(self):
        return f"{self.producto.nombre_producto} x {self.cantidad}" 