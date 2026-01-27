from django.contrib import admin
from .models import Categoria, Plataforma, Juego, Carrito, Pedido, DetallePedido

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'creado']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

@admin.register(Plataforma)
class PlataformaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fabricante', 'creado']
    search_fields = ['nombre', 'fabricante', 'descripcion']
    ordering = ['nombre']

@admin.register(Juego)
class JuegoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'plataforma', 'categoria', 'precio', 'stock', 'rating', 'activo']
    list_filter = ['plataforma', 'categoria', 'activo', 'fecha_lanzamiento']
    search_fields = ['titulo', 'desarrollador', 'descripcion']
    list_editable = ['precio', 'stock', 'activo', 'rating']
    ordering = ['-creado']
    readonly_fields = ['creado', 'actualizado']

    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'descripcion', 'desarrollador', 'fecha_lanzamiento')
        }),
        ('Precio e inventario', {
            'fields': ('precio', 'stock', 'activo')
        }),
        ('Clasificación', {
            'fields': ('plataforma', 'categoria', 'rating')
        }),
        ('Imagen', {
            'fields': ('imagen',)
        }),
        ('Registro', {
            'fields': ('creado', 'actualizado'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'juego', 'cantidad', 'subtotal', 'creado']
    list_filter = ['creado']
    search_fields = ['usuario__username', 'juego__titulo']
    readonly_fields = ['subtotal', 'creado', 'actualizado']

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'total', 'estado', 'creado']
    list_filter = ['estado', 'creado']
    search_fields = ['usuario__username', 'direccion_envio']
    readonly_fields = ['total', 'creado', 'actualizado']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'juego', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['pedido__estado']
    search_fields = ['pedido__id', 'juego__titulo']
    readonly_fields = ['subtotal']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pedido', 'juego')
