from django import forms
from .models import Pedido, Producto, DetallePedido, Client, CrearTicket, Documento, BackOrder, ProductoBackOrder
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class TicketForm(forms.ModelForm):
    """
    TicketForm es un formulario basado en ModelForm para la creación y edición de instancias del modelo CrearTicket.
    Campos:
        - categoria: Campo de selección para la categoría del ticket, renderizado con un widget Select y clase CSS 'form-control'.
        - nivel_prioridad: Campo de selección para el nivel de prioridad del ticket, renderizado con un widget Select y clase CSS 'form-control'.
        - descripcion: Campo de texto para la descripción del ticket, renderizado con un widget Textarea de 4 filas y 40 columnas.
    Este formulario personaliza los widgets de los campos para mejorar la experiencia de usuario en la interfaz.
    """
    
    class Meta:
        model = CrearTicket
        fields = [
            'categoria',
            'nivel_prioridad',
            'descripcion',
            
        ]
        widgets = {
            'descripcion' : forms.Textarea(attrs={'rows':4, 'cols':40}),
            'categoria' : forms.Select(attrs={'class': 'form-control'}),
            'nivel_prioridad' : forms.Select(attrs={'class': 'form-control'})
        }
        

class PedidoForm(forms.ModelForm):
    """
    Formulario de Django para la creación y edición de instancias del modelo Pedido.
    Este formulario utiliza un ModelForm basado en el modelo Pedido, permitiendo la gestión de los siguientes campos:
    - nombre_cliente
    - numero_cliente
    - nombre_contacto
    - calle
    - colonia
    - municipio
    - estado
    - codigo_postal
    - telefono
    - lista_items
    - estatus
    Algunos campos de dirección y teléfono se configuran como solo lectura mediante widgets personalizados.
    El campo 'estatus' utiliza un widget Select con una clase CSS personalizada y se inicializa con el valor predeterminado 'pendiente'.
    Además, se incluye un campo adicional 'cliente', que es un ModelChoiceField requerido para seleccionar una instancia de Client.
    Atributos:
        Meta (class): Define el modelo y los campos asociados al formulario, así como los widgets personalizados.
        cliente (ModelChoiceField): Campo para seleccionar un cliente existente.
    Métodos:
        __init__(*args, **kwargs): Inicializa el formulario y establece el valor inicial del campo 'estatus'.
    """
    
    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'numero_cliente', 'nombre_contacto', 'calle', 'colonia', 'municipio', 'estado', 'codigo_postal', 'telefono', 'lista_items', 'estatus']
        widgets = {
            'calle': forms.TextInput(attrs={'readonly': True}),
            'colonia': forms.TextInput(attrs={'readonly': True}),
            'municipio': forms.TextInput(attrs={'readonly': True}),
            'estado': forms.TextInput(attrs={'readonly': True}),
            'codigo_postal': forms.TextInput(attrs={'readonly': True}),
            'telefono': forms.TextInput(attrs={'readonly': True}),
            'estatus': forms.Select(attrs={'class': 'form-control'})
        }
    # Si quieres asegurarte de que se envíe un valor predeterminado
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estatus'].initial = 'pendiente'  # Valor predeterminado

    cliente = forms.ModelChoiceField(queryset=Client.objects.all(), required=True)
    
class DetallePedidoForm(forms.Form):
    """
    Formulario dinámico para la selección de productos y cantidades en un pedido.
    Este formulario genera campos de cantidad para cada producto disponible, permitiendo al usuario seleccionar la cantidad deseada de cada uno. Los productos pueden ser filtrados por línea si se proporciona el argumento 'linea' al inicializar el formulario.
    Atributos:
        - Los campos de cantidad se crean dinámicamente para cada producto, mostrando información relevante como imagen, nombre, precios y cantidad por caja.
    Métodos:
        __init__(*args, **kwargs):
            Inicializa el formulario, generando los campos de cantidad para cada producto. Si se proporciona una línea de producto, solo se muestran los productos de esa línea.
        clean():
            Valida que al menos un producto tenga una cantidad mayor a cero. Devuelve un diccionario con los IDs de los productos seleccionados y sus cantidades correspondientes.
    Excepciones:
        - forms.ValidationError: Se lanza si no se selecciona ningún producto con cantidad mayor a cero.
    
    """
    
    # Creamos dinámicamente los campos de cantidades
    def __init__(self, *args, **kwargs):
        #Se obtiene linea del producto desde los argumentos
        linea_producto = kwargs.pop('linea', None)
        
        super().__init__(*args, **kwargs)
        
        # Valida si hay filtro aplicado de cierta linea en especifico
        if linea_producto:
            productos = Producto.objects.filter(linea= linea_producto)
        else:
            productos = Producto.objects.all()

        # Por cada producto, crear un campo de cantidad
        for producto in productos:
            self.fields[f'cantidad_{producto.id}'] = forms.IntegerField(
                required=False,
                min_value=0,  # La cantidad puede ser 0, pero no se procesará
                label = mark_safe(
                    f"""
                    <div style='display: flex; flex-direction: column;'>
                        <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                            <img src='{producto.imagen}' alt='{producto.nombre_producto}' 
                                style='width:100px; height:120px; margin-right:20px; border-radius: 5px;' />
                            <div>
                                <strong style='font-size: 1.2em; color: #14438b;'>{producto.nombre_producto}</strong>
                            </div>
                        </div>
                        <div style='font-size: 0.9em; margin-bottom: 5px;'>
                            <span>Diamante: <strong>${producto.precio_2}</strong></span> - 
                            <span>Oro: <strong>${producto.precio_1}</strong></span>
                        </div>
                        <div style='font-size: 0.9em; color: #555;'>
                            La caja contiene <strong>{producto.qty_caja}</strong> productos (Cajas)
                        </div>
                    </div>
                    """
                ),
                initial=None  # Inicializamos la cantidad en 0
            )

    def clean(self):
        cleaned_data = super().clean()
        
        # Recolectamos los productos seleccionados y sus cantidades
        productos_seleccionados = []
        cantidades = {}
        
        for producto_id in Producto.objects.values_list('id', flat=True):
            cantidad = cleaned_data.get(f'cantidad_{producto_id}')
            if cantidad and cantidad > 0:  # Solo procesar productos con cantidad > 0
                productos_seleccionados.append(producto_id)
                cantidades[producto_id] = cantidad
        
        # Validar si al menos un producto tiene cantidad mayor a 0
        if not productos_seleccionados:
            raise forms.ValidationError("Debes agregar al menos un producto con cantidad mayor a 0.")
        
        return {'productos': productos_seleccionados, 'cantidades': cantidades}
    
class CambiarContraseniaForm(forms.Form):
    """
    Formulario para cambiar la contraseña de un usuario.
    Campos:
        old_password (CharField): Contraseña actual del usuario.
        new_password1 (CharField): Nueva contraseña que el usuario desea establecer.
        new_password2 (CharField): Confirmación de la nueva contraseña.
    Validaciones:
        - Verifica que los campos 'new_password1' y 'new_password2' coincidan.
        - Lanza un ValidationError si las nuevas contraseñas no coinciden.
    Uso:
        Este formulario se utiliza para solicitar al usuario su contraseña actual y la nueva contraseña (dos veces para confirmación) al momento de realizar un cambio de contraseña.
    """
    
    old_password = forms.CharField(
        label="Contraseña Actual",
        widget=forms.PasswordInput,
        required=True
    )
    new_password1 = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput,
        required=True
    )
    new_password2 = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput,
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("Las nuevas contraseñas no coinciden.")

class CambiarEmailForm(forms.Form):
    """
    Formulario para cambiar la dirección de correo electrónico de un usuario.
    Campos:
        new_email (EmailField): Campo requerido para ingresar el nuevo correo electrónico.
    """
    
    new_email = forms.EmailField(
        label="Nuevo Correo Electrónico",
        required=True
    )
    
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'archivo']  # Campos del formulario
        
class BuscarFacturaForm(forms.Form):
    """
    Formulario para buscar una factura por su número de folio.
    Campos:
        folio (CharField): Campo de texto para ingresar el número de folio de la factura a buscar.
            - Etiqueta: 'Número de Folio'
            - Longitud máxima: 20 caracteres
            - Widget: TextInput con placeholder 'Ej: FOL-12345' y clase CSS 'form-control'
    """
    
    folio = forms.CharField(
        label='Número de Folio',
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: FOL-12345',
            'class': 'form-control'
        })
    )

class ProductoBackOrderForm(forms.Form):
    """
    Formulario para gestionar productos en backorder.
    Este formulario recopila la información necesaria para registrar un producto pendiente de entrega (backorder) en el sistema de ventas. Incluye los siguientes campos:
    Atributos:
        codigo (CharField): Código identificador del producto. Obligatorio, máximo 50 caracteres.
        producto (CharField): Descripción del producto. Obligatorio, máximo 255 caracteres.
        cantidad_pendiente (IntegerField): Cantidad pendiente del producto. Obligatorio, valor mínimo de 1.
    Cada campo incluye validaciones y mensajes de error personalizados para mejorar la experiencia del usuario.
    """
    
    codigo = forms.CharField(
        label='Código',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Código del producto'
        }),
        error_messages={
            'required': 'El código del producto es obligatorio'
        }
    )
    
    producto = forms.CharField(
        label='Descripción',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Descripción del producto'
        }),
        error_messages={
            'required': 'La descripción del producto es obligatoria'
        }
    )
    
    cantidad_pendiente = forms.IntegerField(
        label='Cantidad Pendiente',
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cantidad',
            'min': '1'
        }),
        error_messages={
            'required': 'La cantidad es obligatoria',
            'min_value': 'La cantidad mínima es 1'
        }
    )