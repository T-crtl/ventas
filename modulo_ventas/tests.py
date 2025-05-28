from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Client, Pedido, Directorio, DetallePedido, CrearTicket, Producto, Factura, ProductoFactura, BackOrder, ProductoBackOrder

# Create your tests here.
class ClientModelTest(TestCase):

    def setUp(self):
        """
        Configura el entorno de prueba creando una instancia de un cliente con datos ficticios.
        Este método se ejecuta antes de cada prueba para asegurar que exista un objeto Client
        con información de ejemplo, permitiendo realizar pruebas sobre funcionalidades que
        dependan de la existencia de clientes en la base de datos.
        Atributos creados:
            self.client (Client): Instancia del modelo Client con datos de prueba.
        """
        
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
        """
        Testea la creación correcta de un cliente.
        Este test verifica que los atributos 'nombre_cliente', 'rfc' y 'clasificacion'
        del objeto 'client' sean asignados correctamente al crear un nuevo cliente.
        Asserts:
            - El nombre del cliente es "Juan Pérez".
            - El RFC del cliente es "PERJ123456ABC".
            - La clasificación del cliente es "LOCAL".
        """        
        """Prueba que un cliente se crea correctamente."""
        self.assertEqual(self.client.nombre_cliente, "Juan Pérez")
        self.assertEqual(self.client.rfc, "PERJ123456ABC")
        self.assertEqual(self.client.clasificacion, "LOCAL")

    def test_client_str_representation(self):
        """
        Prueba que la representación en cadena (__str__) del modelo Client
        retorne el nombre completo del cliente correctamente.
        Este test verifica que al convertir una instancia de Client a cadena,
        el resultado sea igual a "Juan Pérez".
        """
        
        """Prueba la representación en cadena del modelo."""
        self.assertEqual(str(self.client), "Juan Pérez")

    def test_client_verbose_name(self):
        """
        Prueba que los atributos 'verbose_name' y 'verbose_name_plural' del modelo Client
        sean los valores esperados ('Cliente' y 'Clientes', respectivamente).
        Esto asegura que los nombres legibles definidos en el modelo sean correctos
        para su uso en la interfaz de administración y otros contextos de Django.
        """
        
        """Prueba los nombres legibles (verbose_name) del modelo."""
        self.assertEqual(Client._meta.verbose_name, 'Cliente')
        self.assertEqual(Client._meta.verbose_name_plural, 'Clientes')
        
class PedidoModelTest(TestCase):
    """
    TestCase para el modelo Pedido.
    Esta clase contiene pruebas unitarias para verificar la correcta creación y representación
    en cadena de los objetos del modelo Pedido. Utiliza datos de prueba para instancias de
    Cliente y User, y valida que los atributos del pedido se asignen correctamente y que la
    representación en cadena (__str__) del modelo sea la esperada.
    Métodos:
        setUp(): Configura los datos de prueba necesarios para cada test.
        test_pedido_creation(): Verifica que un pedido se cree con los valores correctos.
        test_pedido_str_representation(): Verifica la representación en cadena del pedido.
    """

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
    """
    TestCase para el modelo DetallePedido.
    Esta clase contiene pruebas unitarias para verificar la correcta creación de instancias
    del modelo DetallePedido y el cálculo de su subtotal. Utiliza datos de prueba para los
    modelos relacionados como Cliente, User, Pedido y Producto.
    Métodos:
        setUp(): Configura los datos de prueba necesarios para cada test.
        test_detalle_pedido_creation(): Verifica que el detalle del pedido se crea correctamente
            y que los campos relacionados contienen los valores esperados.
        test_calcular_subtotal(): Prueba que el método calcular_subtotal del modelo DetallePedido
            retorna el valor correcto basado en la cantidad y el precio del producto.
    """
    
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
    """
    TestCase para el modelo CrearTicket.
    Esta clase contiene pruebas unitarias para verificar la correcta creación de instancias del modelo CrearTicket.
    Incluye la configuración de datos de prueba y un método de prueba para asegurar que los atributos del ticket
    se asignan correctamente al momento de su creación.
    Métodos:
        setUp(): Configura un usuario y un ticket de prueba antes de cada test.
        test_ticket_creation(): Verifica que los campos del ticket se establecen correctamente.
    """

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
    """
    TestCase para el modelo Directorio.
    Esta clase contiene pruebas unitarias para verificar la correcta creación y atributos
    de instancias del modelo Directorio. Utiliza datos de prueba definidos en el método setUp
    y valida que los campos del modelo se asignen correctamente al crear un nuevo documento.
    Métodos:
        setUp():
            Configura una instancia de Directorio con datos de prueba antes de cada prueba.
        test_directorio_creation():
            Verifica que los atributos del documento creado coincidan con los valores esperados.
    """

    def setUp(self):
        """
        Configura el entorno de prueba creando una instancia de Directorio con datos de ejemplo.
        Este método se ejecuta antes de cada prueba para asegurar que exista un objeto Directorio
        con valores predefinidos, permitiendo así realizar pruebas sobre funcionalidades que
        dependen de este modelo.
        Atributos creados:
            self.documento (Directorio): Instancia de Directorio creada para pruebas.
        """
        
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

class FacturaModelTest(TestCase):
    
    def setUp(self):
        # Configura datos de prueba
        self.factura = Factura.objects.create(
            cve_doc="FAC-001",
            folio='1234',
            factura = 'F001',
            cliente_clave='CLI-001',
            cliente_nombre='Juan Pérez',
            rfc = 'JPE123456789',
            direccion = 'Calle Falsa 123',
        )
        
        ProductoFactura.objects.create(
            folio=self.factura,
            id_articulo='ART-001',
            nombre_articulo='Producto Test',
            cantidad_solicitada=10,
            lote_asignado='L001',
            cantidad_real= 10,
        )
        ProductoFactura.objects.create(
            folio=self.factura,
            id_articulo='ART-002',
            nombre_articulo='Producto Test 2',
            cantidad_solicitada=5,
            lote_asignado='L002',
            cantidad_real= 5,
        )

    def test_factura_str(self):
        self.assertEqual(str(self.factura), "Factura F001 (Folio: 1234) ")

    def test_productos_completos_count(self):
        self.assertEqual(self.factura.productos_completos, 2)
    
    def test_relacion_porductos_factura(self):
        self.assertEqual(self.factura.productos.count(), 2)
