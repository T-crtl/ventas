from django import forms
from .models import Pedido, Producto, DetallePedido, Client, CrearTicket, Documento, BackOrder, ProductoBackOrder
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class TicketForm(forms.ModelForm):
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
    new_email = forms.EmailField(
        label="Nuevo Correo Electrónico",
        required=True
    )
    
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'archivo']  # Campos del formulario
        
class BuscarFacturaForm(forms.Form):
    folio = forms.CharField(
        label='Número de Folio',
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej: FOL-12345',
            'class': 'form-control'
        })
    )

class ProductoBackOrderForm(forms.ModelForm):
    class Meta:
        model = ProductoBackOrder
        fields = ['lote_asignado', 'cantidad_real']
        widgets = {
            'lote_asignado': forms.TextInput(attrs={
                'placeholder': 'Ej: LOTE-001',
                'class': 'form-control'
            }),
            'cantidad_real': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            })
        }