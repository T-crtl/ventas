from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/profile/', views.profile, name='profile'),  # Ruta para el perfil
    path('realizar_pedido/', views.realizar_pedido, name='realizar_pedido'),
    path('ver_estatus_pedido/', views.ver_estatus_pedido, name='ver_estatus_pedido'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('accounts/profile/ajustes/', views.perfil_empleado, name='perfil_empleado'),
    path('obtener_datos_cliente/', views.obtener_datos_cliente, name='obtener_datos_cliente'),
    path('ticket_it/', views.ticket, name='realizar_ticket'),
    path('ver_ticket/', views.ver_ticket, name='ver_estatus_ticket'),
    path('resolver_ticket/', views.admin_it, name='cerrar_ticket'),
    path('ticket/<int:ticket_id>/', views.detalle_ticket_it, name='detalle_ticket'),
    path('ticket/<int:ticket_id>/cambiar_estado/', views.cambiar_estado_ticket, name='cambiar_estado_ticket'),
    path('directorios/', views.directorio, name='directorios'),
    path('sistemas_directorio/', views.sistemas_dir, name='sistemas_dir'),
    path('administracion_dir/', views.administracion_dir, name= 'administracion_dir'),
    path('cobranza_dir/', views.cobranza_dir, name='cobranza_dir'),
    path('asistente_dir/', views.asistente_dir, name='asistente_dir'),
    path('compras_dir/', views.compras_dir, name='compras_dir'),
    path('produccion_dir/', views.produccion_dir, name='produccion_dir'),
    path('ventas_dir/', views.ventas_dir, name='ventas_dir'),
    path('rh_dir/', views.rh_dir, name='rh_dir'),
    path('formulaciones_dir/', views.formulaciones_dir, name='formulaciones_dir'),
    path('imagen_dir/', views.imagen_dir, name='imagen_dir'),
    path('community_dir/', views.community_dir, name='community_dir'),
    path('recepcion_dir/', views.recepcion_dir, name='recepcion_dir'),
    path('calidad_dir/', views.calidad_dir, name='calidad_dir'),
    path('proyectos_dir/', views.proyectos_dir, name='proyectos_dir'),
    path('ceo_dir/', views.ceo_dir, name='ceo_dir'),
    path('blb_dir/', views.blb_dir, name='blb_dir'),
]
