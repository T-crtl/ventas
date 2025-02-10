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
]
