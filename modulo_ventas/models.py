import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Client(models.Model):
    
    CLASIF_CHOICES = [
        ('FORANEO', 'FORANEO'),
        ('LOCAL', 'LOCAL'),
    ]
    
    clave_cliente = models.BigIntegerField(unique=True)
    nombre_cliente = models.CharField(verbose_name='Nombre de cliente' ,max_length=255, null=True, blank=True)
    rfc = models.CharField(verbose_name='rfc de cliente',max_length=255, null=True, blank=True)
    calle = models.CharField(verbose_name='calle',max_length=255, null=True, blank=True)
    numint = models.CharField(verbose_name='numero interior', max_length=255, null=True, blank=True)
    numext = models.CharField(verbose_name='numero exterior' ,max_length=255, null=True, blank=True)
    colonia = models.CharField(verbose_name='Nombre de colonia',max_length=255, null=True, blank=True)
    codigo = models.CharField(verbose_name='codigo postal' ,null=True, blank=True, max_length=5)
    municipio = models.CharField(verbose_name='nombre de municipio', max_length=255, null=True, blank=True)
    estado = models.CharField(verbose_name='nombre de estado', max_length=255, null=True, blank=True)
    pais = models.CharField(verbose_name='nombre pais' ,max_length=255, blank=True, null=True)
    telefono = models.CharField(verbose_name='numero de telefono' ,max_length=255, blank=True, null=True)
    clasificacion = models.CharField(
        max_length=20,
        choices=CLASIF_CHOICES,
        null=True,
        blank=True,
    ) 
    curp = models.CharField(verbose_name='curp de cliente' ,max_length=18, null=True, blank= True)
    email = models.EmailField(verbose_name='email cliente' ,max_length=255, null=True, blank=True)   
    
    def __str__(self):
        return self.nombre_cliente  
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre_cliente']

class Pedido(models.Model):
    ESTATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('enviado', 'Enviado'),
    ]

    nombre_cliente = models.ForeignKey(Client, on_delete=models.CASCADE)
    numero_cliente = models.IntegerField(default=0, null=True, blank=True)
    nombre_contacto = models.CharField(max_length=255, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    calle = models.CharField(max_length=255, null=True, blank=True)
    colonia = models.CharField(max_length=255, null=True, blank=True)
    municipio = models.CharField(max_length=255, null=True, blank=True)
    estado = models.CharField(max_length=255, null=True, blank=True)
    codigo_postal = models.CharField(max_length=10, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
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
    
class CrearTicket(models.Model):
    TICKET = [
    ('hardware', 'HARDWARE'),
    ('software', 'SOFTWARE'),
    ('wifi', 'WIFI'),
    ('servidor', 'SERVIDOR'),
    ('redes', 'REDES'),
    ('seguridad', 'SEGURIDAD'),
    ('correo', 'CORREO ELECTRÓNICO'),
    ('base_de_datos', 'BASE DE DATOS'),
    ('aplicaciones', 'APLICACIONES ESPECÍFICAS'),
    ('impresion', 'IMPRESIÓN'),
    ('telefonia', 'TELEFONÍA/VOIP'),
    ('soporte_usuario', 'SOPORTE A USUARIOS'),
    ('backup', 'BACKUP/RECUPERACIÓN'),
]
    ESTADO = [
        ('abierto', 'ABIERTO'),
        ('en_prograso', 'EN PROGRESO'),
        ('pendiente', 'ESPERANDO RESPUESTO DE UN TERCERO'),
        ('resuelto', 'RESUELTO'),
        ('cerrado', 'CERRADO'),
    ]
    numero_ticket = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre_usuario =  models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='abierto'
    )
    categoria = models.CharField(
        max_length=20,
        choices=TICKET,
        default='soporte_usuario'
    )
    descripcion = models.TextField()
    

    
    