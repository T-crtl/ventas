from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PedidoForm, DetallePedidoForm
from .models import Pedido, DetallePedido, Producto
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator

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
    pedidos = Pedido.objects.filter(vendedor=request.user).order_by('-fecha_creacion')  # Solo pedidos del vendedor actual
    
    numero_cliente = request.GET.get('numero_cliente', '')
    fecha_creacion = request.GET.get('fecha_creacion', '')
    estatus = request.GET.get('estatus', '')

    # Aplicar filtros si los parámetros están presentes
    if numero_cliente:
        pedidos = pedidos.filter(numero_cliente__icontains=numero_cliente)
    if fecha_creacion:
        try:
            # Convertir la fecha de la cadena a un objeto date
            fecha = datetime.strptime(fecha_creacion, '%Y-%m-%d').date()
            # Convertir la fecha naive a una fecha consciente de la zona horaria
            fecha = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
            
            # Filtrar pedidos que se crearon en esa fecha sin importar la hora
            pedidos = pedidos.filter(fecha_creacion__gte=fecha, fecha_creacion__lt=fecha + timedelta(days=1))
            print(f"Fecha recibida: {fecha}")
        except ValueError:
            print("Formato de fecha no válido")
    
    if estatus:
        pedidos = pedidos.filter(estatus__icontains=estatus)
        
    # Configura el paginador
    paginator = Paginator(pedidos, 10)  # 10 resultados por página

    # Obtén el número de página de la URL (?page=1)
    page_number = request.GET.get('page')
    
    # Obtén los resultados de la página actual
    page_obj = paginator.get_page(page_number)
    
    #Contador de cuantos resultados arrojo la busqueda en total
    contador = pedidos.count()
    
    return render(request, 'ver_estatus_pedido.html', {
        'pedidos': page_obj,
        'contador': contador,
        })

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
    
@login_required
def perfil_empleado(request):
    user = request.user
    return render(request, 'perfil_empleado.html', {'user': user})