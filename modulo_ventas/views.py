from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PedidoForm, DetallePedidoForm, TicketForm
from .models import Pedido, DetallePedido, Producto, Client, CrearTicket
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string

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
     # Obtener la línea de producto seleccionada del GET
    linea_producto = request.GET.get('linea_producto', None)

    # Cargar todos los productos o los productos de la línea seleccionada
    productos = Producto.objects.filter(linea=linea_producto) if linea_producto else Producto.objects.all()
    # Obtener los IDs de los productos filtrados
    ids_productos = [producto.id for producto in productos]

    # Verificar si es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            cantidades = {
                producto_id: request.GET.get(f'cantidad_{producto_id}', '')
                for producto_id in ids_productos
                if request.GET.get(f'cantidad_{producto_id}', '')
            }
            html = render_to_string('partials/productos.html', {'productos': productos}, request=request)
            return JsonResponse({
                'html': html,
                'ids_productos': ids_productos,
                'cantidades': cantidades,
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.method == 'POST':
        # Formularios de pedido y detalle
        form_pedido = PedidoForm(request.POST)
        form_detalle = DetallePedidoForm(request.POST, linea=linea_producto)
        print(request.POST) 
        if form_pedido.is_valid() and form_detalle.is_valid():
            # Guardar el pedido
            pedido = form_pedido.save(commit=False)  # Guardamos el pedido sin confirmar aún
            pedido.vendedor = request.user  # Asigna el vendedor (el usuario actual)
            
            # Obtener y asociar el cliente
            cliente = form_pedido.cleaned_data['cliente']
            pedido.cliente = cliente  # Asocia el cliente al pedido

            # Si se necesita actualizar la información del cliente, se hace aquí:
            cliente.calle = form_pedido.cleaned_data['calle']
            cliente.colonia = form_pedido.cleaned_data['colonia']
            cliente.municipio = form_pedido.cleaned_data['municipio']
            cliente.estado = form_pedido.cleaned_data['estado']
            cliente.codigo_postal = form_pedido.cleaned_data['codigo_postal']
            cliente.telefono = form_pedido.cleaned_data['telefono']
            cliente.save()  # Guarda los cambios en el cliente

            # Guarda el pedido
            pedido.save()

            # Guardar los detalles del pedido
            productos_seleccionados = form_detalle.cleaned_data['productos']
            cantidades = form_detalle.cleaned_data['cantidades']

            for producto_id in productos_seleccionados:
                producto = get_object_or_404(Producto, id=producto_id)
                cantidad = cantidades[producto_id]
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                )

            return redirect('ver_estatus_pedido')  # Redirige al estatus del pedido
        else:
            print(f"{form_pedido.is_valid()}, {form_detalle.is_valid()}")
            print(f"Errores del formulario de pedido: {form_pedido.errors}")
    else:
        # Carga los formularios vacíos o con datos previos
        form_pedido = PedidoForm()
        form_detalle = DetallePedidoForm(linea=linea_producto)

    # Pasamos `linea_producto` y `productos` al contexto
    return render(request, 'realizar_pedido.html', {
        'form_pedido': form_pedido,
        'linea_producto': linea_producto,
        'ids_productos': ids_productos,
        'productos': productos,  # Pasamos los productos al contexto
    })
    
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

@login_required
def obtener_datos_cliente(request):
    # Obtenemos el cliente_id desde la solicitud GET
    cliente_id = request.GET.get('cliente_id')
    
    # Si se proporciona un cliente_id
    if cliente_id:
        try:
            cliente = Client.objects.get(id=cliente_id)  # Obtenemos el cliente desde la base de datos
            # Devolvemos los datos del cliente como JSON
            if not cliente.numint:
                codigo = f"{cliente.numext}"
            else:
                codigo = f"{cliente.numext} {cliente.numint}"
            data = {
                'cliente': cliente.id,
                'numero_cliente': cliente.clave_cliente,
                'calle': cliente.calle,
                'colonia': cliente.colonia,
                'municipio': cliente.municipio,
                'estado': cliente.estado,
                'codigo': codigo,
                'email': cliente.email,
                'telefono_cliente': cliente.telefono,
            }
            return JsonResponse(data)
        except Client.DoesNotExist:
            return JsonResponse({'error': 'Cliente no encontrado'}, status=404)  # Error si el cliente no existe
    return JsonResponse({'error': 'ID de cliente no proporcionado'}, status=400)  # Error si no se proporciona un cliente_id

@login_required
def ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)  # Crea el objeto del modelo pero no lo guarda en la base de datos
            ticket.nombre_usuario = request.user  # Asigna el usuario autenticado
            ticket.save()  # Guarda el ticket en la base de datos
            return redirect('ver_estatus_ticket')  # Redirige a la página de perfil o a donde desees
    else:
        form = TicketForm()
        
    return render(request, 'crear_ticket.html', {'form': form})

@login_required
def ver_ticket(request):
    
    tickets = CrearTicket.objects.filter(nombre_usuario=request.user).order_by('-fecha_creacion')
    
    # Configura el paginador
    paginator = Paginator(tickets, 10)  # 10 resultados por página
    # Obtén el número de página de la URL (?page=1)
    page_number = request.GET.get('page')
    # Obtén los resultados de la página actual
    page_obj = paginator.get_page(page_number)
    #Contador de cuantos resultados arrojo la busqueda en total
    contador = tickets.count()
    
    return render(request, 'ver_ticket.html', {
        'tickets': page_obj,
        'contador': contador,
        })