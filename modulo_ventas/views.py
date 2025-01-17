from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PedidoForm, DetallePedidoForm
from .models import Pedido, DetallePedido, Producto
from django.shortcuts import render, get_object_or_404

# Create your views here.
def index(request):
    return render(request, 'index.html')

@login_required
def profile(request):
    # Verificar si el usuario pertenece al grupo "Vendedores"
    es_vendedor = request.user.groups.filter(name='Vendedores').exists()
    
    # Renderizar la plantilla con el contexto adicional
    return render(request, 'profile.html', {
        'user': request.user,
        'es_vendedor': es_vendedor,
    })

@login_required
def realizar_pedido(request):
    # Lógica para realizar pedido
    if request.method == 'POST':
        form_pedido = PedidoForm(request.POST)
        form_detalle = DetallePedidoForm(request.POST)
        
        if form_pedido.is_valid() and form_detalle.is_valid():
            # Guardar el pedido
            pedido = form_pedido.save(commit=False)
            pedido.vendedor = request.user  # Establecer el vendedor como el usuario actual
            pedido.save()

            # Obtener los productos y sus cantidades
            productos_seleccionados = form_detalle.cleaned_data['productos']
            cantidades = form_detalle.cleaned_data['cantidades']

            # Guardar los detalles del pedido (productos y cantidades)
            for producto_id in productos_seleccionados:
                producto = Producto.objects.get(id=producto_id)
                cantidad = cantidades[producto_id]
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad
                )
            
            return redirect('ver_estatus_pedido')  # Redirigir a la página de estatus

    else:
        form_pedido = PedidoForm()
        form_detalle = DetallePedidoForm()

    return render(request, 'realizar_pedido.html', {'form_pedido': form_pedido, 'form_detalle': form_detalle})

@login_required
def ver_estatus_pedido(request):
    # Lógica para ver estatus de pedido
    pedidos = Pedido.objects.filter(vendedor=request.user)  # Solo pedidos del vendedor actual
    return render(request, 'ver_estatus_pedido.html', {'pedidos': pedidos})

@login_required
def detalle_pedido(request, pedido_id):
    # Obtener el pedido con sus detalles o lanzar un error 404 si no existe
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido)
    
    # Inicializar el total
    total = 0
    
    # Iterar sobre los detalles del pedido
    for detalle in detalles:
        # Seleccionar el precio correcto según el valor de lista_items
        if pedido.lista_items == 1:
            precio = detalle.producto.precio_1
        elif pedido.lista_items == 2:
            precio = detalle.producto.precio_2
        elif pedido.lista_items == 3:
            precio = detalle.producto.precio_3
        else:
            precio = 0
        
        # Sumar el subtotal de este detalle (cantidad * precio)
        total += detalle.cantidad * precio
    
    return render(request, 'detalle_pedido.html', {
        'pedido': pedido,
        'detalles': detalles,
        'total': total,
    })