from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/profile/', views.profile, name='profile'),  # Ruta para el perfil
    path('realizar_pedido/', views.realizar_pedido, name='realizar_pedido'),
    path('ver_estatus_pedido/', views.ver_estatus_pedido, name='ver_estatus_pedido'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
]
