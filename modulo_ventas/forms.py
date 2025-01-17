from django import forms
from .models import Pedido, Producto, DetallePedido
from django.utils.safestring import mark_safe


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'numero_cliente', 'nombre_contacto', 'calle', 'numero', 'colonia', 'municipio', 'estado', 'codigo_postal', 'telefono', 'lista_items']

class DetallePedidoForm(forms.Form):
    # Creamos dinámicamente los campos de productos y cantidades
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Obtener todos los productos disponibles
        productos = Producto.objects.all()
        
        # Por cada producto, crear un campo de selección y cantidad
        for producto in productos:
            self.fields[f'imagen_{producto.id}'] = forms.CharField(
                required=False, 
                label=mark_safe(f"<img src='{producto.imagen}' alt='{producto.nombre_producto}' "
                    f"style='width:200px; height:200px; margin-right:10px;' /> "), 
                widget=forms.TextInput(attrs={'readonly': 'readonly', 'style': 'border:none; background:none;'})
            )
            self.fields[f'producto_{producto.id}'] = forms.BooleanField(
                required=False, label=f"{producto.nombre_producto}", initial=False
            )
            self.fields[f'precio_{producto.id}'] =  forms.CharField(
                required=False, 
                label=mark_safe(f"Diamante ${producto.precio_1} - Oro ${producto.precio_2}"), 
                widget=forms.TextInput(attrs={'readonly': 'readonly', 'style': 'border:none; background:none;'})
            )
            self.fields[f'cantidad_{producto.id}'] = forms.IntegerField(
                min_value=0, initial=0, label=f"Selecciona la cantidad de cajas - ",
                required=False
            )
            
    def clean(self):
        cleaned_data = super().clean()
        
        # Recolectamos los productos seleccionados y las cantidades
        productos_seleccionados = []
        cantidades = {}
        
        for producto_id in Producto.objects.values_list('id', flat=True):
            if cleaned_data.get(f'producto_{producto_id}', False):
                cantidad = cleaned_data.get(f'cantidad_{producto_id}')
                if cantidad:
                    productos_seleccionados.append(producto_id)
                    cantidades[producto_id] = cantidad
        
        # Validar si al menos un producto ha sido seleccionado
        if not productos_seleccionados:
            raise forms.ValidationError("Debes seleccionar al menos un producto.")
        
        return {'productos': productos_seleccionados, 'cantidades': cantidades}