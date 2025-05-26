import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Client(models.Model):
    """
    Modelo Client
    Representa la información de un cliente en el sistema de ventas.
    Atributos:
        clave_cliente (BigIntegerField): Clave única del cliente.
        nombre_cliente (CharField): Nombre del cliente.
        rfc (CharField): RFC del cliente.
        calle (CharField): Calle de la dirección del cliente.
        numint (CharField): Número interior de la dirección.
        numext (CharField): Número exterior de la dirección.
        colonia (CharField): Colonia de la dirección.
        codigo (CharField): Código postal.
        municipio (CharField): Municipio de la dirección.
        estado (CharField): Estado de la dirección.
        pais (CharField): País de la dirección.
        telefono (CharField): Número de teléfono del cliente.
        clasificacion (CharField): Clasificación del cliente (FORANEO o LOCAL).
        curp (CharField): CURP del cliente.
        email (EmailField): Correo electrónico del cliente.
    Métodos:
        __str__(): Retorna el nombre del cliente como representación en texto.
    Meta:
        verbose_name: Nombre singular para el modelo en el admin de Django.
        verbose_name_plural: Nombre plural para el modelo en el admin de Django.
        ordering: Ordena los clientes por nombre_cliente.
    """
    
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
    """
    Modelo Pedido representa una orden de venta realizada por un vendedor.
    Atributos:
        nombre_cliente (ForeignKey): Referencia al cliente que realiza el pedido (modelo Client).
        numero_cliente (IntegerField): Número identificador del cliente (opcional).
        nombre_contacto (CharField): Nombre de la persona de contacto para el pedido (opcional).
        fecha_creacion (DateTimeField): Fecha y hora en que se creó el pedido (asignado automáticamente).
        calle (CharField): Calle de la dirección de entrega (opcional).
        colonia (CharField): Colonia de la dirección de entrega (opcional).
        municipio (CharField): Municipio de la dirección de entrega (opcional).
        estado (CharField): Estado de la dirección de entrega (opcional).
        codigo_postal (CharField): Código postal de la dirección de entrega (opcional).
        telefono (CharField): Teléfono de contacto para el pedido (opcional).
        lista_items (IntegerField): Número de listas de items en el pedido (valores posibles: 1, 2, 3).
        estatus (CharField): Estado actual del pedido ('pendiente', 'en_proceso', 'enviado').
        vendedor (ForeignKey): Usuario vendedor asociado al pedido (opcional).
    Métodos:
        __str__(): Retorna una representación legible del pedido, mostrando el cliente y el estatus.
    """
    
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
    """
    Modelo Producto que representa un producto en el sistema de ventas.
    Atributos:
        nombre_producto (CharField): Nombre del producto.
        qty_caja (IntegerField): Cantidad de unidades por caja. Valor por defecto: 0.
        linea (CharField): Línea a la que pertenece el producto. Opciones: 'inbelleza', 'barber', 'platinum', 'none'. Valor por defecto: 'none'.
        precio_1 (FloatField): Primer precio del producto. Valor por defecto: 0.
        precio_2 (FloatField): Segundo precio del producto. Valor por defecto: 0.
        precio_3 (FloatField): Tercer precio del producto. Valor por defecto: 0.
        imagen (CharField): Ruta o nombre de la imagen asociada al producto. Puede ser nulo o estar en blanco.
    Métodos:
        __str__(): Retorna el nombre del producto como representación en cadena del objeto.
    """
    
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
    """
    Modelo que representa el detalle de un pedido, enlazando un producto específico a un pedido y especificando la cantidad solicitada.
    Atributos:
        pedido (ForeignKey): Referencia al pedido al que pertenece este detalle.
        producto (ForeignKey): Referencia al producto incluido en el detalle.
        cantidad (PositiveIntegerField): Cantidad del producto solicitada en el pedido.
    Métodos:
        calcular_subtotal():
            Calcula el subtotal del detalle del pedido, seleccionando el precio del producto según la lista de precios asociada al pedido.
            Retorna el resultado de multiplicar la cantidad por el precio correspondiente.
        __str__():
            Retorna una representación legible del detalle, mostrando el nombre del producto y la cantidad solicitada.
    """
    
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def calcular_subtotal(self):
        """
        Calcula el subtotal de un ítem en el pedido según la lista de precios seleccionada.
        El método determina el precio del producto basado en el valor de 'lista_items' del pedido:
            - Si 'lista_items' es 1, usa 'precio_1' del producto.
            - Si 'lista_items' es 2, usa 'precio_2' del producto.
            - Si 'lista_items' es 3, usa 'precio_3' del producto.
            - Para cualquier otro valor, el precio es 0.
        Retorna:
            float: El subtotal calculado como la cantidad del producto multiplicada por el precio seleccionado.
        """
                
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
    """
    Modelo CrearTicket para la gestión de tickets de soporte en el sistema de ventas.
    Campos:
        numero_ticket (UUIDField): Identificador único del ticket, generado automáticamente.
        fecha_creacion (DateTimeField): Fecha y hora de creación del ticket.
        nombre_usuario (ForeignKey): Referencia al usuario que crea el ticket. Puede ser nulo o estar en blanco.
        estado (CharField): Estado actual del ticket. Opciones: 'abierto', 'en progreso', 'pendiente', 'resuelto', 'cerrado'.
        categoria (CharField): Categoría del ticket. Opciones incluyen hardware, software, wifi, servidor, redes, seguridad, correo electrónico, base de datos, aplicaciones específicas, impresión, telefonía/VOIP, soporte a usuarios, backup/recuperación.
        descripcion (TextField): Descripción detallada del problema o solicitud.
        nivel_prioridad (CharField): Nivel de prioridad del ticket. Opciones: 'critica', 'alta', 'media', 'baja'.
    Constantes de clase:
        TICKET: Lista de tuplas con las categorías disponibles para los tickets.
        ESTADO: Lista de tuplas con los estados posibles del ticket.
        PRIORIDAD: Lista de tuplas con los niveles de prioridad disponibles.
    Uso:
        Este modelo permite registrar y gestionar tickets de soporte, clasificándolos por categoría, estado y prioridad, y asociándolos a un usuario específico.
    """
    
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
        ('en progreso', 'EN PROGRESO'),
        ('pendiente', 'ESPERANDO RESPUESTO DE UN TERCERO'),
        ('resuelto', 'RESUELTO'),
        ('cerrado', 'CERRADO'),
    ]
    
    PRIORIDAD = [
        ('critica', 'Crítica (Alta Prioridad)'),
        ('alta', 'ALTA'),
        ('media', 'MEDIA'),
        ('baja', 'BAJA'),
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
    nivel_prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD,
        default='baja',
    )
    
class Directorio(models.Model):
    """
    Modelo Directorio para gestionar documentos en la aplicación de ventas.
    Atributos:
        TIPO_DOCUMENTO_CHOICES (list): Opciones para el tipo de documento (PDF, Word, Excel, Otro).
        AREA_CHOICES (list): Opciones para el área responsable del documento.
        nombre_documento (CharField): Nombre del documento. Puede ser nulo o estar en blanco.
        area (CharField): Área a la que pertenece el documento. Debe ser una de las opciones definidas en AREA_CHOICES.
        link_documento (URLField): Enlace al documento. Puede ser nulo o estar en blanco.
        tipo_documento (CharField): Tipo de documento. Debe ser una de las opciones definidas en TIPO_DOCUMENTO_CHOICES.
        publico (BooleanField): Indica si el documento es público o no.
    Métodos:
        __str__(): Devuelve el nombre del documento como representación en cadena del objeto.
    """
    
    TIPO_DOCUMENTO_CHOICES = [
        ('PDF', 'PDF'),
        ('WORD', 'Word'),
        ('EXCEL', 'Excel'),
        ('OTRO', 'Otro'),
    ]
    AREA_CHOICES = [
        ('Administracion', 'Administracion'),
        ('Asistente', 'Asistente'),
        ('Cobranza', 'Cobranza'),
        ('Compras', 'Compras'),
        ('Produccion', 'Produccion'),
        ('Ventas', 'Ventas'),
        ('Rh', 'Rh'),
        ('Formulaciones', 'Formulaciones'),
        ('Imagen', 'Imagen'),
        ('Community', 'Community'),
        ('Recepcion', 'Recepcion'),
        ('Calidad', 'Calidad'),
        ('Proyectos', 'Proyectos'),
        ('CEO', 'CEO'),
        ('BLB', 'BLB'),
        ('Sistemas', 'Sistemas'),
    ]
    nombre_documento = models.CharField(max_length=255, null=True, blank=True)
    area = models.CharField(max_length=20, choices=AREA_CHOICES, default='publica')
    link_documento = models.URLField(max_length=255, null=True, blank=True)
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES, default='PDF')
    publico = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre_documento
    
class Area(models.Model):
    pass

class Documento(models.Model):
    """
    Modelo que representa un documento subido al sistema.
    Atributos:
        nombre (CharField): Nombre descriptivo del documento.
        archivo (FileField): Archivo asociado al documento, almacenado en la carpeta 'documentos/'.
        fecha_subida (DateField): Fecha en la que se subió el documento (asignada automáticamente al crear el registro).
    Métodos:
        __str__(): Devuelve el nombre del documento como representación en cadena.
    """
    
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(upload_to='documentos/')
    fecha_subida = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
class Factura(models.Model):
    """
    Modelo que representa una factura en el sistema de ventas.
    Atributos:
        cve_doc (CharField): Clave única del documento de la factura.
        doc_sig (CharField): Documento siguiente relacionado, puede ser nulo o estar en blanco.
        folio (CharField): Folio de la factura.
        factura (CharField): Número o identificador de la factura.
        cliente_clave (CharField): Clave única del cliente asociado a la factura.
        cliente_nombre (CharField): Nombre del cliente.
        rfc (CharField): RFC del cliente, puede ser nulo o estar en blanco.
        fecha_creacion (DateField): Fecha de creación de la factura, asignada automáticamente.
        direccion (TextField): Dirección del cliente.
    Métodos:
        __str__(): Retorna una representación legible de la factura.
        productos_completos (property): Devuelve la cantidad de productos asociados a la factura que tienen lote asignado y cantidad real definida.
    """
    
    cve_doc = models.CharField(max_length=20, unique=True)
    doc_sig = models.CharField(max_length=20, blank=True, null=True)
    folio = models.CharField(max_length=20)
    factura = models.CharField(max_length=20)
    cliente_clave = models.CharField(max_length=30)
    cliente_nombre = models.CharField(max_length=100)
    rfc = models.CharField(max_length=20, blank=True, null=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    direccion = models.TextField()
    
    def __str__(self):
        return f"Factura {self.factura} (Folio: {self.folio}) "
    
    @property
    def productos_completos(self):
        return self.productos.filter(
            lote_asignado__isnull=False,
            cantidad_real__isnull=False
        ).count()

class ProductoFactura(models.Model):
    """
    Modelo que representa un producto incluido en una factura.
    Atributos:
        folio (ForeignKey): Referencia a la factura a la que pertenece el producto.
        id_articulo (CharField): Identificador único del artículo.
        nombre_articulo (CharField): Nombre descriptivo del artículo.
        cantidad_solicitada (FloatField): Cantidad solicitada del artículo en la factura.
        lote_asignado (CharField): Lote asignado al artículo (opcional).
        cantidad_real (FloatField): Cantidad real entregada del artículo (opcional).
        comentaros (TextField): Comentarios adicionales sobre el producto (opcional).
    Métodos:
        __str__(): Retorna una representación legible del producto en la factura.
    """

    folio = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='productos')
    id_articulo = models.CharField(max_length=20)
    nombre_articulo = models.CharField(max_length=100)
    cantidad_solicitada = models.FloatField()
    lote_asignado = models.CharField(max_length=50, blank=True, null=True)
    cantidad_real = models.FloatField(blank=True, null=True)
    comentaros = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.id_articulo} - {self.nombre_articulo}"
    
class BackOrder(models.Model):
    """
    Modelo BackOrder representa un pedido pendiente en el sistema de ventas.
    Atributos:
        folio (CharField): Identificador único del backorder.
        cliente_nombre (CharField): Nombre del cliente asociado al backorder.
        rfc (CharField): Registro Federal de Contribuyentes del cliente.
        direccion (TextField): Dirección del cliente.
        cliente_clave (CharField): Clave interna del cliente (opcional).
        fecha_creacion (DateTimeField): Fecha y hora de creación del backorder.
        check_status (BooleanField): Indica si el backorder ha sido revisado o no.
    Métodos:
        __str__(): Devuelve una representación legible del backorder, mostrando el folio y el nombre del cliente.
    """
    
    folio = models.CharField(max_length=50)
    cliente_nombre = models.CharField(max_length=255)
    rfc = models.CharField(max_length=20)
    direccion = models.TextField()
    cliente_clave = models.CharField(max_length=50, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    check_status = models.BooleanField(default=False)
    
    def __str__(self):
        return f"BackOrder {self.folio} - {self.cliente_nombre}"

class ProductoBackOrder(models.Model):
    """
    Modelo que representa un producto incluido en un BackOrder.
    Atributos:
        factura (ForeignKey): Referencia al BackOrder al que pertenece el producto.
        codigo (CharField): Código identificador del producto.
        descripcion (CharField): Descripción detallada del producto.
        cantidad (DecimalField): Cantidad solicitada del producto.
        cantidad_real (DecimalField, opcional): Cantidad real entregada del producto (puede ser nula).
        lote (CharField, opcional): Lote al que pertenece el producto (puede ser nulo).
    Métodos:
        __str__(): Retorna una representación legible del producto, mostrando su código y descripción.
    """
    
    factura = models.ForeignKey(BackOrder, related_name='productos_backorder', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_real = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    lote = models.CharField(max_length=20, null=True)
    
    
    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"
    
    

    
    

    
    