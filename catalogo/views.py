from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Juego, Categoria, Plataforma, Carrito, Pedido, DetallePedido

def catalogo(request):
    juegos = Juego.objects.filter(activo=True).select_related('plataforma', 'categoria')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    plataforma_id = request.GET.get('plataforma')
    search = request.GET.get('search')
    
    if categoria_id:
        juegos = juegos.filter(categoria_id=categoria_id)
    if plataforma_id:
        juegos = juegos.filter(plataforma_id=plataforma_id)
    if search:
        juegos = juegos.filter(
            Q(titulo__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(desarrollador__icontains=search)
        )
    
    categorias = Categoria.objects.all()
    plataformas = Plataforma.objects.all()
    
    context = {
        'juegos': juegos,
        'categorias': categorias,
        'plataformas': plataformas,
        'categoria_actual': categoria_id,
        'plataforma_actual': plataforma_id,
        'search_actual': search or '',
    }
    return render(request, 'catalogo/catalogo.html', context)

def detalle_juego(request, juego_id):
    juego = get_object_or_404(Juego, id=juego_id, activo=True)
    juegos_relacionados = Juego.objects.filter(
        categoria=juego.categoria,
        activo=True
    ).exclude(id=juego.id)[:4]
    
    context = {
        'juego': juego,
        'juegos_relacionados': juegos_relacionados,
    }
    return render(request, 'catalogo/detalle_juego.html', context)

@login_required
def agregar_al_carrito(request, juego_id):
    juego = get_object_or_404(Juego, id=juego_id, activo=True)
    
    if not juego.disponible:
        messages.error(request, 'Este juego no está disponible actualmente.')
        return redirect('catalogo:detalle_juego', juego_id=juego_id)
    
    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user,
        juego=juego,
        defaults={'cantidad': 1}
    )
    
    if not created:
        if carrito.cantidad < juego.stock:
            carrito.cantidad += 1
            carrito.save()
            messages.success(request, f'"{juego.titulo}" agregado al carrito.')
        else:
            messages.error(request, 'No hay suficiente stock disponible.')
    else:
        messages.success(request, f'"{juego.titulo}" agregado al carrito.')
    
    return redirect('catalogo:carrito')

@login_required
def carrito(request):
    items = Carrito.objects.filter(usuario=request.user).select_related('juego')
    total = sum(item.subtotal for item in items)
    
    context = {
        'items': items,
        'total': total,
    }
    return render(request, 'catalogo/carrito.html', context)

@login_required
def actualizar_carrito(request, item_id):
    item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
    cantidad = request.POST.get('cantidad', 1)
    
    try:
        cantidad = int(cantidad)
        if cantidad > 0 and cantidad <= item.juego.stock:
            item.cantidad = cantidad
            item.save()
            messages.success(request, 'Carrito actualizado.')
        else:
            messages.error(request, 'Cantidad no válida o insuficiente stock.')
    except ValueError:
        messages.error(request, 'Cantidad no válida.')
    
    return redirect('catalogo:carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
    item.delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('catalogo:carrito')

@login_required
def checkout(request):
    items = Carrito.objects.filter(usuario=request.user).select_related('juego')
    
    if not items:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('catalogo:carrito')
    
    total = sum(item.subtotal for item in items)
    
    if request.method == 'POST':
        direccion = request.POST.get('direccion')
        notas = request.POST.get('notas', '')
        
        if not direccion:
            messages.error(request, 'Por favor ingresa una dirección de envío.')
            return render(request, 'catalogo/checkout.html', {
                'items': items,
                'total': total,
            })
        
        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total,
            direccion_envio=direccion,
            notas=notas,
            estado='pendiente'
        )
        
        # Crear detalles del pedido y actualizar stock
        for item in items:
            DetallePedido.objects.create(
                pedido=pedido,
                juego=item.juego,
                cantidad=item.cantidad,
                precio_unitario=item.juego.precio
            )
            # Actualizar stock
            item.juego.stock -= item.cantidad
            item.juego.save()
        
        # Vaciar carrito
        items.delete()
        
        messages.success(request, f'Pedido #{pedido.id} creado exitosamente.')
        return redirect('catalogo:confirmacion_pedido', pedido_id=pedido.id)
    
    context = {
        'items': items,
        'total': total,
    }
    return render(request, 'catalogo/checkout.html', context)

@login_required
def confirmacion_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    detalles = pedido.detalles.all().select_related('juego')
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
    }
    return render(request, 'catalogo/confirmacion_pedido.html', context)

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-creado')
    
    context = {
        'pedidos': pedidos,
    }
    return render(request, 'catalogo/mis_pedidos.html', context)
