from django import forms
from .models import Pedido, Producto, DetallePedido
from django.utils.safestring import mark_safe


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'numero_cliente', 'nombre_contacto', 'calle', 'numero', 'colonia', 'municipio', 'estado', 'codigo_postal', 'telefono', 'lista_items']

class DetallePedidoForm(forms.Form):
    # Creamos dinámicamente los campos de cantidades
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Obtener todos los productos disponibles
        productos = Producto.objects.all()
        
        # Por cada producto, crear un campo de cantidad
        for producto in productos:
            self.fields[f'cantidad_{producto.id}'] = forms.IntegerField(
                required=False,
                min_value=0,  # La cantidad puede ser 0, pero no se procesará
                label=mark_safe(f"<div style='display: flex; align-items: center;'>"
                                f"<img src='{producto.imagen}' alt='{producto.nombre_producto}' "
                                f"style='width:80px; height:100px; margin-right:20px;' />"
                                f"{producto.nombre_producto}</div>"
                                f"<div>Diamante ${producto.precio_1} - Oro ${producto.precio_2}</div>"
                                f"La caja contiene {producto.qty_caja} productos (Cajas): "),
                initial=0  # Inicializamos la cantidad en 0
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