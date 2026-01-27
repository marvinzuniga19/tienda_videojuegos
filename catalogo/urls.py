from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('juego/<int:juego_id>/', views.detalle_juego, name='detalle_juego'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:juego_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedido/confirmacion/<int:pedido_id>/', views.confirmacion_pedido, name='confirmacion_pedido'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
]