from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PedidoForm, DetallePedidoForm, TicketForm, CambiarContraseniaForm, CambiarEmailForm
from .models import Pedido, DetallePedido, Producto, Client, CrearTicket, Directorio
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from uuid import UUID
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.contrib import messages
import requests

# Create your views here.
def index(request):
    return render(request, 'index.html')

@login_required
def profile(request):
    # Verificar si el usuario pertenece al grupo "Vendedores"
    es_vendedor = request.user.groups.filter(name='Vendedores').exists()
    admin_it = request.user.groups.filter(name='ADMIN').exists()
    
    # Renderizar la plantilla con el contexto adicional
    return render(request, 'profile.html', {
        'user': request.user,
        'es_vendedor': es_vendedor,
        'it': admin_it,
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
    
    # Obtener los filtros desde la URL
    numero_ticket_filtro = request.GET.get('ticket', '')
    estado_filtro = request.GET.get('estado', '')
    fecha_filtro = request.GET.get('fecha_creacion', '')
    
    # Aplicar los filtros si existen
    if numero_ticket_filtro:
        try:
            # Convertir el valor del filtro a UUID
            uuid_filtro = UUID(numero_ticket_filtro)
            #print(f"UUID a buscar: {uuid_filtro}")  # Depuración
            tickets = tickets.filter(numero_ticket=uuid_filtro)
            #print(f"Tickets filtrados: {tickets.count()}")  # Depuración
        except ValueError:
            # Si el valor no es un UUID válido, ignora el filtro
            print("UUID de ticket no válido")
        
    if estado_filtro:
        tickets = tickets.filter(estado__icontains=estado_filtro)

    if fecha_filtro:
        try:
            # Convertir la fecha de la cadena a un objeto date
            fecha = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            # Convertir la fecha naive a una fecha consciente de la zona horaria
            fecha = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
            
            # Filtrar tickets que se crearon en esa fecha sin importar la hora
            tickets = tickets.filter(fecha_creacion__gte=fecha, fecha_creacion__lt=fecha + timedelta(days=1))
            print(f"Fecha recibida: {fecha}")
        except ValueError:
            print("Formato de fecha no válido")
    print(f"Número de ticket filtro: {numero_ticket_filtro}")  # Depuración       
    # Configura el paginador
    paginator = Paginator(tickets, 10)  # 10 resultados por página
    # Obtén el número de página de la URL (?page=1)
    page_number = request.GET.get('page')
    # Obtén los resultados de la página actual
    page_obj = paginator.get_page(page_number)
    # Contador de cuantos resultados arrojo la busqueda en total
    contador = tickets.count()
    
    return render(request, 'ver_ticket.html', {
        'tickets': page_obj,
        'contador': contador,
        'numero_ticket_filtro': numero_ticket_filtro,
        'fecha_filtro': fecha_filtro,
        'estado_filtro': estado_filtro,
    })
    
@login_required
def admin_it(request):
     # Obtener todos los tickets ordenados por fecha de creación (más recientes primero)
    tickets = CrearTicket.objects.all().order_by('-fecha_creacion')

    # Verifica si el usuario pertenece al grupo IT
    if not request.user.groups.filter(name='ADMIN').exists():
        raise PermissionDenied("No tienes permiso para cambiar el estado del ticket.")
    
    # Obtener los filtros desde la URL
    numero_ticket_filtro = request.GET.get('ticket', '')
    estado_filtro = request.GET.get('estado', '')
    fecha_filtro = request.GET.get('fecha_creacion', '')

    # Aplicar los filtros si existen
    if numero_ticket_filtro:
        try:
            # Convertir el valor del filtro a UUID
            uuid_filtro = UUID(numero_ticket_filtro)
            #print(f"UUID a buscar: {uuid_filtro}")  # Depuración
            tickets = tickets.filter(numero_ticket=uuid_filtro)
            #print(f"Tickets filtrados: {tickets.count()}")  # Depuración
        except ValueError:
            # Si el valor no es un UUID válido, ignora el filtro
            print("UUID de ticket no válido")
            
    if estado_filtro:
        tickets = tickets.filter(estado__icontains=estado_filtro)

    if fecha_filtro:
        try:
            # Convertir la fecha de la cadena a un objeto date
            fecha = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
            # Convertir la fecha naive a una fecha consciente de la zona horaria
            fecha = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
            
            # Filtrar tickets que se crearon en esa fecha sin importar la hora
            tickets = tickets.filter(fecha_creacion__gte=fecha, fecha_creacion__lt=fecha + timedelta(days=1))
            print(f"Fecha recibida: {fecha}")
        except ValueError:
            print("Formato de fecha no válido")

    # Paginación
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    contador = tickets.count()

    return render(request, 'tickets_it.html', {
        'tickets': page_obj,
        'contador': contador,
        'estado_filtro': estado_filtro,
        'fecha_filtro': fecha_filtro,
        'numero_ticket_filtro': numero_ticket_filtro,
    })

@login_required
def detalle_ticket_it(request, ticket_id):
    ticket = get_object_or_404(CrearTicket, id=ticket_id)
    admin_it = request.user.groups.filter(name='ADMIN').exists()
    # Verifica si el usuario es parte del equipo de IT
    if not request.user.groups.filter(name='ADMIN').exists():
        raise PermissionDenied("No tienes permiso para ver este ticket.")
    
    
    return render(request, 'ver_ticket_detalle.html', {
        'ticket': ticket,
        'it': admin_it,
    })
    
def cambiar_estado_ticket(request, ticket_id):
    ticket = get_object_or_404(CrearTicket, id=ticket_id)

    # Verifica si el usuario pertenece al grupo IT
    if not request.user.groups.filter(name='ADMIN').exists():
        raise PermissionDenied("No tienes permiso para cambiar el estado del ticket.")

    # Define la lógica para cambiar el estado al siguiente
    ESTADOS = ['abierto', 'en progreso', 'resuelto', 'cerrado']
    if ticket.estado in ESTADOS:
        siguiente_estado_idx = ESTADOS.index(ticket.estado) + 1
        if siguiente_estado_idx < len(ESTADOS):  # Evita pasarse de "Cerrado"
            ticket.estado = ESTADOS[siguiente_estado_idx]
            ticket.save()

    return redirect('detalle_ticket', ticket_id=ticket.id)

@login_required
def directorio(request):
    # Obtener el grupo del usuario
    user_groups = request.user.groups.values_list('name', flat=True)
    
    # Verificar si el usuario pertenece a algún grupo específico
    is_administracion = 'Administracion' in user_groups
    is_asistente = 'Asistente' in user_groups
    is_sistemas = 'ADMIN' in user_groups
    is_cobranza = 'Cobranza' in user_groups
    is_compras = 'Compras' in user_groups
    is_produccion = 'Produccion' in user_groups
    is_ventas = 'Ventas' in user_groups
    is_rh = 'Rh' in user_groups
    is_formulaciones = 'Formulaciones' in user_groups
    is_imagen = 'Imagen' in user_groups
    is_community = 'Community' in user_groups
    is_recepcion = 'Recepcion' in user_groups
    is_calidad = 'Calidad' in user_groups
    is_proyectos = 'Proyectos' in user_groups
    is_ceo = 'Ceo' in user_groups
    # Agrega más verificaciones según tus grupos...

    # Pasar el contexto a la plantilla
    return render(request, 'directorios.html', {
        'is_administracion': is_administracion,
        'is_asistente': is_asistente,
        'is_sistemas': is_sistemas,
        'is_cobranza': is_cobranza,
        'is_compras' : is_compras,
        'is_produccion' : is_produccion,
        'is_ventas' : is_ventas,
        'is_rh' : is_rh,
        'is_formulaciones' : is_formulaciones,
        'is_imagen' : is_imagen,
        'is_community' : is_community,
        'is_recepcion' : is_recepcion,
        'is_calidad' : is_calidad,
        'is_proyectos' : is_proyectos,
        'is_ceo' : is_ceo
        # Agrega más variables de contexto según tus grupos...
    })
    
def sistemas_dir(request):
    directorios = Directorio.objects.filter(area= 'Sistemas')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def administracion_dir(request):
    directorios = Directorio.objects.filter(area= 'Administracion')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

def cobranza_dir(request):
    directorios = Directorio.objects.filter(area= 'Cobranza')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def asistente_dir(request):
    directorios = Directorio.objects.filter(area= 'Asistente')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

def compras_dir(request):
    directorios = Directorio.objects.filter(area= 'Compras')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def produccion_dir(request):
    directorios = Directorio.objects.filter(area= 'Produccion')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def ventas_dir(request):
    directorios = Directorio.objects.filter(area= 'Ventas')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

def rh_dir(request):
    directorios = Directorio.objects.filter(area= 'Rh')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def formulaciones_dir(request):
    directorios = Directorio.objects.filter(area= 'Formulaciones')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def imagen_dir(request):
    directorios = Directorio.objects.filter(area= 'Imagen')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def community_dir(request):
    directorios = Directorio.objects.filter(area= 'Community')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def recepcion_dir(request):
    directorios = Directorio.objects.filter(area= 'Recepcion')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def calidad_dir(request):
    directorios = Directorio.objects.filter(area= 'Calidad')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def proyectos_dir(request):
    directorios = Directorio.objects.filter(area= 'Proyectos')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def ceo_dir(request):
    directorios = Directorio.objects.filter(area= 'CEO')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
def blb_dir(request):
    directorios = Directorio.objects.filter(area= 'BLB')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
@login_required
def cambiar_contrasenia(request):
    if request.method == 'POST':
        form = CambiarContraseniaForm(request.POST)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password1 = form.cleaned_data['new_password1']

            # Verificar que la contraseña actual es correcta
            if not check_password(old_password, user.password):
                messages.error(request, 'La contraseña actual es incorrecta.')
            else:
                # Cambiar la contraseña
                user.set_password(new_password1)
                user.save()
                # Actualizar la sesión para evitar que el usuario se desconecte
                update_session_auth_hash(request, user)
                messages.success(request, '¡Tu contraseña ha sido cambiada exitosamente!')
                return redirect('perfil_empleado')
    else:
        form = CambiarContraseniaForm()

    return render(request, 'cambiar_contrasenia.html', {'form': form})


@login_required
def cambiar_email(request):
    if request.method == 'POST':
        form = CambiarEmailForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            user = request.user
            user.email = new_email
            user.save()
            messages.success(request, '¡Tu correo electrónico ha sido actualizado exitosamente!')
            return redirect('perfil_empleado')
    else:
        form = CambiarEmailForm()

    return render(request, 'cambiar_email.html', {'form': form})

def vista_404(request, exception=None):
    return render(request, '404.html', status=404)

def vista_403(request, exception=None):
    return render(request, '403.html', status=403)

def buscar_cantidad(request):
    """""
    Busca la cantidad de un lote en la base de datos.
    :param cvelote: Clave del lote a buscar.
    :return: Cantidad del lote o None si no se encuentra.
    """""
    # Lógica de la función
    cvelote = request.GET.get('cvelote')
    error = None
    cantidad = None

    if cvelote:
        try:
            # URL de la API de FastAPI (usando la URL pública de ngrok)
            api_url = f'https://3b1f-129-222-90-213.ngrok-free.app/buscar_cantidad/?cvelote={cvelote}'

            # Llamar a la API de FastAPI con el encabezado personalizado
            headers = {
                'ngrok-skip-browser-warning': 'true'  # Agregar este encabezado
            }
            response = requests.get(api_url, headers=headers)

            # Verificar si la API devolvió un resultado válido
            if response.status_code == 200:
                datos = response.json()
                cantidad = datos['cantidad']
            else:
                error = 'Error al obtener los datos del lote'

        except Exception as e:
            error = str(e)
    else:
        error = 'Ingrese una clave de lote'

    # Renderizar la plantilla con los datos
    return render(request, 'resultado.html', {
        'cvelote': cvelote,
        'cantidad': cantidad,
        'error': error,
    })