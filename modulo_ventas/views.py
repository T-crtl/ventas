from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PedidoForm, DetallePedidoForm, TicketForm, CambiarContraseniaForm, CambiarEmailForm, DocumentoForm
from .models import Pedido, DetallePedido, Producto, Client, CrearTicket, Directorio, Documento, Factura, ProductoFactura, ProductoBackOrder, BackOrder
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
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Count
from django.views.decorators.http import require_POST
from .forms import BuscarFacturaForm, ProductoBackOrderForm

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
            # Enviar correo electrónico
            # subject = f'Nuevo Ticket Creado: {ticket.numero_ticket}'
            # message = (
            #     f'Se ha creado un nuevo ticket con los siguientes detalles:\n\n'
            #     f'Número de Ticket: {ticket.numero_ticket}\n'
            #     f'Categoría: {ticket.get_categoria_display()}\n'
            #     f'Descripción: {ticket.descripcion}\n'
            #     f'Prioridad: {ticket.get_nivel_prioridad_display()}\n'
            #     f'Estado: {ticket.get_estado_display()}\n'
            #     f'Fecha de Creación: {ticket.fecha_creacion}\n'
            #     f'Usuario: {ticket.nombre_usuario.username}'
            # )
            # from_email = settings.EMAIL_HOST_USER
            # recipient_list = ['sistemas@blb.mx']  # Cambia esto por el correo del destinatario

            #send_mail(subject, message, from_email, recipient_list)

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

@login_required    
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
    # Diccionario que mapea grupos a directorios permitidos
    grupos_directorios = {
        'Administracion': ['administracion_dir', 'cobranza_dir', 'compras_dir'],
        'Asistente': ['asistente_dir'],
        'ADMIN': ['sistemas_dir', 'administracion_dir', 'asistente_dir', 'cobranza_dir', 'compras_dir', 'produccion_dir', 'ventas_dir', 'rh_dir', 'formulaciones_dir', 'imagen_dir', 'community_dir', 'recepcion_dir', 'calidad_dir', 'proyectos_dir', 'ceo_dir'],
        'Cobranza': ['cobranza_dir'],
        'Compras': ['compras_dir'],
        'Produccion': ['produccion_dir'],
        'Ventas': ['ventas_dir'],
        'Rh': ['rh_dir'],
        'Formulaciones': ['formulaciones_dir'],
        'Imagen': ['imagen_dir', 'community_dir'],
        'Community': ['community_dir', 'imagen_dir'],
        'Recepcion': ['recepcion_dir'],
        'Calidad': ['calidad_dir'],
        'Proyectos': ['proyectos_dir'],
        'Ceo': ['sistemas_dir', 'administracion_dir', 'asistente_dir', 'cobranza_dir', 'compras_dir', 'produccion_dir', 'ventas_dir', 'rh_dir', 'formulaciones_dir', 'imagen_dir', 'community_dir', 'recepcion_dir', 'calidad_dir', 'proyectos_dir', 'ceo_dir'],
    }

    # Obtener los grupos del usuario
    user_groups = request.user.groups.values_list('name', flat=True)

    # Determinar los directorios permitidos para el usuario
    directorios_permitidos = set()
    for group in user_groups:
        if group in grupos_directorios:
            directorios_permitidos.update(grupos_directorios[group])

    # Lista de todos los directorios disponibles
    todos_directorios = [
        {'nombre': 'SISTEMAS', 'url': 'sistemas_dir'},
        {'nombre': 'ADMINISTRACION', 'url': 'administracion_dir'},
        {'nombre': 'ASISTENTE', 'url': 'asistente_dir'},
        {'nombre': 'COBRANZA', 'url': 'cobranza_dir'},
        {'nombre': 'COMPRAS', 'url': 'compras_dir'},
        {'nombre': 'PRODUCCION', 'url': 'produccion_dir'},
        {'nombre': 'VENTAS', 'url': 'ventas_dir'},
        {'nombre': 'RH', 'url': 'rh_dir'},
        {'nombre': 'FORMULACIONES', 'url': 'formulaciones_dir'},
        {'nombre': 'IMAGEN', 'url': 'imagen_dir'},
        {'nombre': 'COMMUNITY', 'url': 'community_dir'},
        {'nombre': 'RECEPCION', 'url': 'recepcion_dir'},
        {'nombre': 'CALIDAD', 'url': 'calidad_dir'},
        {'nombre': 'PROYECTOS', 'url': 'proyectos_dir'},
        {'nombre': 'CEO', 'url': 'ceo_dir'},
    ]

    # Filtrar los directorios permitidos
    directorios_filtrados = [dir for dir in todos_directorios if dir['url'] in directorios_permitidos]

    # Pasar el contexto a la plantilla
    return render(request, 'directorios.html', {
        'directorios': directorios_filtrados,
        'is_sistemas': 'ADMIN' in user_groups,  # Solo si necesitas esta variable para otros usos
    })

@login_required    
def sistemas_dir(request):
    directorios = Directorio.objects.filter(area= 'Sistemas')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
@login_required    
def administracion_dir(request):
    directorios = Directorio.objects.filter(area= 'Administracion')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
@login_required
def cobranza_dir(request):
    directorios = Directorio.objects.filter(area= 'Cobranza')
    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
@login_required    
def asistente_dir(request):
    directorios = Directorio.objects.filter(area= 'Asistente')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
@login_required
def compras_dir(request):
    directorios = Directorio.objects.filter(area= 'Compras')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })
    
@login_required    
def produccion_dir(request):
    directorios = Directorio.objects.filter(area= 'Produccion')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required    
def ventas_dir(request):
    directorios = Directorio.objects.filter(area= 'Ventas')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required
def rh_dir(request):
    directorios = Directorio.objects.filter(area= 'Rh')
    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required    
def formulaciones_dir(request):
    directorios = Directorio.objects.filter(area= 'Formulaciones')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required    
def imagen_dir(request):
    directorios = Directorio.objects.filter(area= 'Imagen')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required    
def community_dir(request):
    directorios = Directorio.objects.filter(area= 'Community')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required    
def recepcion_dir(request):
    directorios = Directorio.objects.filter(area= 'Recepcion')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required    
def calidad_dir(request):
    directorios = Directorio.objects.filter(area= 'Calidad')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required    
def proyectos_dir(request):
    directorios = Directorio.objects.filter(area= 'Proyectos')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required    
def ceo_dir(request):
    directorios = Directorio.objects.filter(area= 'CEO')

    return render(request, 'template_dir.html', {
        'directorios' : directorios,
    })

@login_required    
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

@login_required
def buscar_por_folio(request):
    """
    Busca información de factura por FOLIO usando la API FastAPI
    y guarda los datos en los modelos Factura y ProductoFactura
    """
    if request.method == 'GET':
        folio = request.GET.get('folio')
        error = None
        factura_api_data = None

        if folio:
            try:
                api_url = f'https://95c1-129-222-90-213.ngrok-free.app/buscar_por_folio/?folio={folio}'
                headers = {'ngrok-skip-browser-warning': 'true'}
                response = requests.get(api_url, headers=headers)

                if response.status_code == 200:
                    datos = response.json()
                    facturas_api = datos.get('resultados', [])
                    
                    if facturas_api:
                        # Procesar la primera factura para obtener datos del cliente
                        primera_factura = facturas_api[0]
                        
                        # Crear dirección completa
                        direccion_completa = (
                            f"{primera_factura['CALLE']} {primera_factura['NUMEXT']} "
                            f"{'Int. ' + primera_factura['NUMINT'] if primera_factura['NUMINT'] else ''}, "
                            f"{primera_factura['COLONIA']}, {primera_factura['CP']}, "
                            f"{primera_factura['MUNICIPIO']}, {primera_factura['ESTADO']}"
                        )
                        
                        # Preparar datos para mostrar (sin guardar aún)
                        factura_data = {
                            'cve_doc': primera_factura['CVE_DOC'].strip(),
                            'doc_sig': primera_factura['DOC_SIG'],
                            'folio': str(primera_factura['FOLIO']),
                            'factura': primera_factura['FACTURA'],
                            'cliente_clave': primera_factura['Clave_Cliente'].strip(),
                            'cliente_nombre': primera_factura['Nombre_Cliente'],
                            'rfc': primera_factura['RFC'],
                            'direccion': direccion_completa,
                            'productos': []
                        }
                        
                        for producto_api in facturas_api:
                            factura_data['productos'].append({
                                'id_articulo': producto_api['idARTICULO'],
                                'nombre_articulo': producto_api['NOMBRE DEL ARTICULO'],
                                'cantidad_solicitada': producto_api['PRODUCTOS SOLICITADOS']
                            })
                        
                        # Guardar datos en sesión para posible guardado posterior
                        request.session['factura_temp'] = factura_data
                        
                        return render(request, 'resultado_factura.html', {
                            'folio': folio,
                            'factura_data': factura_data,
                            'error': error,
                            'existe_en_bd': Factura.objects.filter(cve_doc=factura_data['cve_doc']).exists()
                        })
                    else:
                        error = 'No se encontraron facturas con ese folio'
                elif response.status_code == 404:
                    error = 'Folio no encontrado'
                else:
                    error = f'Error al consultar la API: {response.status_code}'

            except requests.exceptions.RequestException as e:
                error = f'Error de conexión con la API: {str(e)}'
            except Exception as e:
                error = f'Error inesperado: {str(e)}'
        else:
            error = 'Ingrese un número de folio'
        
        return render(request, 'resultado_factura.html', {
            'folio': folio,
            'error': error,
        })
    
    elif request.method == 'POST':
        factura_data = request.session.get('factura_temp')
        if not factura_data:
            messages.error(request, 'No hay datos de factura para guardar. Realice una búsqueda primero.')
            return redirect('buscar_por_folio')  # Ajusta esto al nombre de tu URL
        
        # Verificar si la factura ya existe
        if Factura.objects.filter(cve_doc=factura_data['cve_doc']).exists():
            messages.warning(request, 'Esta factura ya existe en la base de datos')
            return render(request, 'resultado_factura.html', {
                'factura_data': factura_data,
                'existe_en_bd': True
            })
        
        # Crear la factura y los productos
        try:
            factura = Factura.objects.create(
                cve_doc=factura_data['cve_doc'],
                doc_sig=factura_data['doc_sig'],
                folio=factura_data['folio'],
                factura=factura_data['factura'],
                cliente_clave=factura_data['cliente_clave'],
                cliente_nombre=factura_data['cliente_nombre'],
                rfc=factura_data['rfc'],
                direccion=factura_data['direccion']
            )
            
            for producto in factura_data['productos']:
                ProductoFactura.objects.create(
                    folio=factura,
                    id_articulo=producto['id_articulo'],
                    nombre_articulo=producto['nombre_articulo'],
                    cantidad_solicitada=producto['cantidad_solicitada']
                )
            
            # Mensaje de éxito
            messages.success(request, f'✅ Factura {factura.factura} guardada correctamente con {len(factura_data["productos"])} productos')
            
            # Limpiar datos temporales y redirigir
            if 'factura_temp' in request.session:
                del request.session['factura_temp']
            return redirect('buscar_por_folio')  # Ajusta esto al nombre de tu URL
        
        except Exception as e:
            messages.error(request, f'❌ Error al guardar la factura: {str(e)}')
            return render(request, 'resultado_factura.html', {
                'factura_data': factura_data,
                'existe_en_bd': False
            })

@login_required    
def subir_documento(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_documentos')  # Redirige a la lista de documentos
    else:
        form = DocumentoForm()
    return render(request, 'subir_documento.html', {'form': form})

@login_required
def lista_documentos(request):
    documentos = Documento.objects.all()
    return render(request, 'lista_documentos.html', {'documentos': documentos})

@login_required
def pedidos_almacen(request):
    # Facturas que tienen productos incompletos (sin lote o sin cantidad)
    facturas = Factura.objects.annotate(
        productos_incompletos=Count(
            'productos',
            filter=Q(productos__lote_asignado__isnull=True) | 
            Q(productos__cantidad_real__isnull=True)
        )
    ).filter(productos_incompletos__gt=0).order_by('-fecha_creacion')
    
    # Filtros de búsqueda
    query = request.GET.get('q')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if query:
        facturas = facturas.filter(
            Q(folio__icontains=query) |
            Q(factura__icontains=query) |
            Q(cliente_nombre__icontains=query)
        )
    
    if fecha_inicio:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            facturas = facturas.filter(fecha_creacion__gte=fecha_inicio)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            facturas = facturas.filter(fecha_creacion__lte=fecha_fin)
        except ValueError:
            pass
    
    return render(request, 'almacen_factura.html', {
        'facturas': facturas,
        'search_query': query or '',
        'fecha_inicio': fecha_inicio or '',
        'fecha_fin': fecha_fin or ''
    })

@login_required
def detalle_factura(request, factura_id):
    factura = get_object_or_404(Factura, pk=factura_id)
    
    if request.method == 'POST':
        errores = []
        
        for producto in factura.productos.all():
            lote_key = f'lote_{producto.id}'
            cantidad_key = f'cantidad_{producto.id}'
            
            lote = request.POST.get(lote_key, '').strip()
            cantidad_str = request.POST.get(cantidad_key, '').strip()
            
            # Validación de campos
            if not lote or not cantidad_str:
                errores.append(f"El producto {producto.nombre_articulo} requiere lote y cantidad")
                continue
                
            try:
                cantidad = float(cantidad_str)
                if cantidad <= 0:
                    errores.append(f"Cantidad inválida para {producto.nombre_articulo}")
                    continue
                    
                producto.lote_asignado = lote
                producto.cantidad_real = cantidad
                producto.save()
                
            except ValueError:
                errores.append(f"Cantidad no válida para {producto.nombre_articulo}")
                continue
        
        if errores:
            messages.error(request, "Corrige los siguientes errores:")
            for error in errores:
                messages.error(request, error)
        else:
            messages.success(request, "¡Datos guardados correctamente!")
            return redirect('detalle_factura', factura_id=factura.id)
    
    return render(request, 'detalle_factura.html', {
        'factura': factura,
        'messages': messages.get_messages(request)
    })
    
@login_required
def facturacion_final(request):
    # Facturas donde todos los productos tienen lote y cantidad asignados
    facturas_completas = Factura.objects.annotate(
        productos_pendientes=Count(
            'productos',
            filter=Q(productos__lote_asignado__isnull=True) | 
            Q(productos__cantidad_real__isnull=True)
        )
    ).filter(productos_pendientes=0).order_by('-fecha_creacion')
    
    return render(request, 'facturacion_final.html', {
        'facturas': facturas_completas
    })
    
@login_required
def crear_backorder(request):
    """
    Vista para crear backorders, integrando:
    1. Formulario Django para búsqueda
    2. Conexión con API externa
    3. Creación de registros en DB
    """
    context = {
        'error': None,
        'folio': request.GET.get('folio', ''),
        'factura_data': None,
        'productos_manuales': request.session.get('productos_manuales', [])
    }

    # --- BÚSQUEDA DE FACTURA (GET) ---
    if request.method == 'GET' and context['folio']:
        try:
            # Consulta a tu API
            api_url = f'https://95c1-129-222-90-213.ngrok-free.app/buscar_por_folio/?folio={context["folio"]}'
            response = requests.get(api_url, headers={'ngrok-skip-browser-warning': 'true'})

            if response.status_code == 200:
                datos_api = response.json().get('resultados', [])
                
                if datos_api:
                    primera_factura = datos_api[0]
                    
                    # Estructura de datos para el template
                    context['factura_data'] = {
                        'folio': str(primera_factura['FOLIO']),
                        'cliente_nombre': primera_factura['Nombre_Cliente'],
                        'rfc': primera_factura['RFC'],
                        'direccion': (
                            f"{primera_factura['CALLE']} {primera_factura['NUMEXT']} "
                            f"{'Int. ' + primera_factura['NUMINT'] if primera_factura['NUMINT'] else ''}, "
                            f"{primera_factura['COLONIA']}, {primera_factura['CP']}, "
                            f"{primera_factura['MUNICIPIO']}, {primera_factura['ESTADO']}"
                        ),
                        'productos_api': [
                            {
                                'id_articulo': p['idARTICULO'],
                                'nombre': p['NOMBRE DEL ARTICULO'],
                                'cantidad': p['PRODUCTOS SOLICITADOS']
                            } for p in datos_api
                        ]
                    }
                    request.session['factura_data'] = context['factura_data']
                else:
                    context['error'] = 'No se encontraron facturas con ese folio'
            else:
                context['error'] = f'Error en API: {response.status_code}'

        except Exception as e:
            context['error'] = f'Error: {str(e)}'

    # --- AGREGAR PRODUCTO MANUAL (POST) ---
    elif request.method == 'POST' and 'agregar_producto' in request.POST:
        producto_manual = {
            'id_articulo': request.POST.get('id_manual', '').strip(),
            'nombre': request.POST.get('nombre_manual', '').strip(),
            'cantidad': float(request.POST.get('cantidad_manual', 0))
        }
        
        if producto_manual['id_articulo'] and producto_manual['nombre']:
            productos_manuales = request.session.get('productos_manuales', [])
            productos_manuales.append(producto_manual)
            request.session['productos_manuales'] = productos_manuales
            context['productos_manuales'] = productos_manuales

    # --- GUARDAR BACKORDER (POST) ---
    elif request.method == 'POST' and 'guardar_backorder' in request.POST:
        try:
            factura_data = request.session.get('factura_data')
            productos_manuales = request.session.get('productos_manuales', [])
            
            if not factura_data:
                raise ValueError("No hay datos de factura para guardar")

            # Crear BackOrder
            backorder = BackOrder.objects.create(
                folio_original=factura_data['folio'],
                cliente_nombre=factura_data['cliente_nombre'],
                rfc=factura_data['rfc'],
                direccion=factura_data['direccion']
            )

            # Guardar productos de API
            for p in factura_data['productos_api']:
                ProductoBackOrder.objects.create(
                    backorder=backorder,
                    id_articulo=p['id_articulo'],
                    nombre_articulo=p['nombre'],
                    cantidad_pendiente=p['cantidad']
                )

            # Guardar productos manuales
            for p in productos_manuales:
                ProductoBackOrder.objects.create(
                    backorder=backorder,
                    id_articulo=p['id_articulo'],
                    nombre_articulo=p['nombre'],
                    cantidad_pendiente=p['cantidad']
                )

            # Limpiar sesión
            del request.session['factura_data']
            del request.session['productos_manuales']
            
            return redirect('surtir_backorder', backorder_id=backorder.id)

        except Exception as e:
            context['error'] = f'Error al guardar: {str(e)}'

    return render(request, 'backorders.html', context)
   

@login_required
def surtir_backorder(request, backorder_id):
    """
    Vista para surtir backorders usando:
    1. Formularios Django por cada producto
    2. Validación automática
    3. Actualización de campos NULL (lote/cantidad)
    """
    backorder = get_object_or_404(BackOrder, id=backorder_id)
    
    if request.method == 'POST':
        forms_validos = True
        
        # Crear diccionario para guardar los forms procesados
        forms_procesados = []
        
        for producto in backorder.productos.all():
            # Usamos prefijos únicos para cada producto
            form = ProductoBackOrderForm(
                request.POST,
                prefix=f"prod_{producto.id}",
                instance=producto
            )
            
            if form.is_valid():
                # Guardamos el form pero NO commit a DB aún
                instancia = form.save(commit=False)
                # Actualizamos fecha solo si se está surtiendo
                if instancia.cantidad_real and not producto.cantidad_real:
                    instancia.fecha_surtido = timezone.now()
                instancia.save()
                forms_procesados.append((producto, form))
            else:
                forms_validos = False
                break
        
        if forms_validos:
            return redirect('detalle_backorder', backorder_id=backorder.id)
    else:
        # Preparar formularios iniciales (GET request)
        forms_procesados = [
            (producto, ProductoBackOrderForm(
                prefix=f"prod_{producto.id}",
                instance=producto,
                initial={
                    'cantidad_real': producto.cantidad_pendiente  # Sugerir cantidad pendiente por defecto
                }
            )) for producto in backorder.productos.all()
        ]
    
    return render(request, 'backorders_surtir.html', {
        'backorder': backorder,
        'forms_productos': forms_procesados
    })