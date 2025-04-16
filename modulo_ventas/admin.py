from django.contrib import admin
from .models import Pedido, Producto, DetallePedido, Client, CrearTicket, Directorio, Area, Documento, Factura, ProductoFactura, BackOrder

# Register your models here.
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('nombre_cliente', 'numero_cliente', 'fecha_creacion', 'estatus')  # Campos visibles en la lista
    list_filter = ('fecha_creacion', 'estatus')  # Agregar filtros por fecha y vendedor
    search_fields = ('nombre_cliente', 'numero_cliente')  # Agregar barra de búsqueda
    ordering = ('-fecha_creacion',)  # Ordenar por fecha de creación descendente

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto','linea', 'qty_caja', 'precio_1', 'precio_2', 'precio_3', 'imagen')
    search_fields = ('nombre_producto','linea')
    list_filter = ('linea', 'nombre_producto')
    
@admin.register(DetallePedido) 
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'cantidad')
    
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('clave_cliente', 'nombre_cliente', 'municipio')
    
@admin.register(CrearTicket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('estado', 'fecha_creacion', 'nombre_usuario', 'numero_ticket')

@admin.register(Directorio)
class DirectorioAdmin(admin.ModelAdmin):
    list_display = ('nombre_documento', 'area', 'link_documento', 'tipo_documento')
    
@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'archivo')
    
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('cve_doc', 'folio')
    
@admin.register(ProductoFactura)
class ProductoFacturaAdmin(admin.ModelAdmin):
    list_display = ('folio', 'id_articulo')
    
@admin.register(BackOrder)
class BackorderAdmin(admin.ModelAdmin):
    list_display = ('folio', 'cliente_nombre')