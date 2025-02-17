from django.test import TestCase
from django.contrib.auth.models import User
from .models import Client, Pedido, Directorio, DetallePedido, CrearTicket, Producto

# Create your tests here.
class ClientModelTest(TestCase):

    def setUp(self):
        # Configura datos de prueba
        self.client = Client.objects.create(
            clave_cliente=123456,
            nombre_cliente="Juan Pérez",
            rfc="PERJ123456ABC",
            calle="Calle Falsa",
            numint="123",
            numext="456",
            colonia="Centro",
            codigo="12345",
            municipio="Guadalajara",
            estado="Jalisco",
            pais="México",
            telefono="3312345678",
            clasificacion="LOCAL",
            curp="PERJ123456HDFABC01",
            email="juan@example.com"
        )

    def test_client_creation(self):
        """Prueba que un cliente se crea correctamente."""
        self.assertEqual(self.client.nombre_cliente, "Juan Pérez")
        self.assertEqual(self.client.rfc, "PERJ123456ABC")
        self.assertEqual(self.client.clasificacion, "LOCAL")

    def test_client_str_representation(self):
        """Prueba la representación en cadena del modelo."""
        self.assertEqual(str(self.client), "Juan Pérez")

    def test_client_verbose_name(self):
        """Prueba los nombres legibles (verbose_name) del modelo."""
        self.assertEqual(Client._meta.verbose_name, 'Cliente')
        self.assertEqual(Client._meta.verbose_name_plural, 'Clientes')
        
class PedidoModelTest(TestCase):

    def setUp(self):
        # Configura datos de prueba
        self.client = Client.objects.create(
            clave_cliente=123456,
            nombre_cliente="Juan Pérez"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.pedido = Pedido.objects.create(
            nombre_cliente=self.client,
            numero_cliente=123,
            nombre_contacto="Contacto Test",
            calle="Calle Falsa",
            colonia="Centro",
            municipio="Guadalajara",
            estado="Jalisco",
            codigo_postal="12345",
            telefono="3312345678",
            lista_items=1,
            estatus="pendiente",
            vendedor=self.user
        )

    def test_pedido_creation(self):
        """Prueba que un pedido se crea correctamente."""
        self.assertEqual(self.pedido.nombre_cliente.nombre_cliente, "Juan Pérez")
        self.assertEqual(self.pedido.estatus, "pendiente")
        self.assertEqual(self.pedido.vendedor.username, "testuser")

    def test_pedido_str_representation(self):
        """Prueba la representación en cadena del modelo."""
        self.assertEqual(str(self.pedido), "Pedido Juan Pérez - pendiente")
        
class ProductoModelTest(TestCase):

    def setUp(self):
        # Configura datos de prueba
        self.producto = Producto.objects.create(
            nombre_producto="Producto Test",
            qty_caja=10,
            linea="inbelleza",
            precio_1=100.0,
            precio_2=90.0,
            precio_3=80.0
        )

    def test_producto_creation(self):
        """Prueba que un producto se crea correctamente."""
        self.assertEqual(self.producto.nombre_producto, "Producto Test")
        self.assertEqual(self.producto.linea, "inbelleza")
        self.assertEqual(self.producto.precio_1, 100.0)

    def test_producto_str_representation(self):
        """Prueba la representación en cadena del modelo."""
        self.assertEqual(str(self.producto), "Producto Test")
        
class DetallePedidoModelTest(TestCase):

    def setUp(self):
        # Configura datos de prueba
        self.client = Client.objects.create(
            clave_cliente=123456,
            nombre_cliente="Juan Pérez"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.pedido = Pedido.objects.create(
            nombre_cliente=self.client,
            numero_cliente=123,
            nombre_contacto="Contacto Test",
            lista_items=1,
            estatus="pendiente",
            vendedor=self.user
        )
        self.producto = Producto.objects.create(
            nombre_producto="Producto Test",
            qty_caja=10,
            linea="inbelleza",
            precio_1=100.0
        )
        self.detalle = DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=2
        )

    def test_detalle_pedido_creation(self):
        """Prueba que un detalle de pedido se crea correctamente."""
        self.assertEqual(self.detalle.pedido.nombre_cliente.nombre_cliente, "Juan Pérez")
        self.assertEqual(self.detalle.producto.nombre_producto, "Producto Test")
        self.assertEqual(self.detalle.cantidad, 2)

    def test_calcular_subtotal(self):
        """Prueba el cálculo del subtotal."""
        self.assertEqual(self.detalle.calcular_subtotal(), 200.0)
    
class CrearTicketModelTest(TestCase):

    def setUp(self):
        # Configura datos de prueba
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.ticket = CrearTicket.objects.create(
            nombre_usuario=self.user,
            estado="abierto",
            categoria="soporte_usuario",
            descripcion="Problema con el servidor",
            nivel_prioridad="alta"
        )

    def test_ticket_creation(self):
        """Prueba que un ticket se crea correctamente."""
        self.assertEqual(self.ticket.nombre_usuario.username, "testuser")
        self.assertEqual(self.ticket.estado, "abierto")
        self.assertEqual(self.ticket.nivel_prioridad, "alta")
        
class DirectorioModelTest(TestCase):

    def setUp(self):
        # Configura datos de prueba
        self.documento = Directorio.objects.create(
            nombre_documento="Documento Test",
            area="Administracion",
            link_documento="https://example.com/documento.pdf",
            tipo_documento="PDF",
            publico=True
        )

    def test_directorio_creation(self):
        """Prueba que un documento se crea correctamente."""
        self.assertEqual(self.documento.nombre_documento, "Documento Test")
        self.assertEqual(self.documento.area, "Administracion")
        self.assertTrue(self.documento.publico)