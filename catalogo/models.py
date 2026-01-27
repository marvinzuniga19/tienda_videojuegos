from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Plataforma(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    fabricante = models.CharField(max_length=100, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Juego(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    plataforma = models.ForeignKey(Plataforma, on_delete=models.CASCADE, related_name='juegos')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='juegos')
    imagen = models.ImageField(upload_to='juegos/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    fecha_lanzamiento = models.DateField()
    desarrollador = models.CharField(max_length=200)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.titulo} ({self.plataforma.nombre})"
    
    @property
    def disponible(self):
        return self.stock > 0 and self.activo

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carritos')
    juego = models.ForeignKey(Juego, on_delete=models.CASCADE, related_name='carritos')
    cantidad = models.PositiveIntegerField(default=1)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['usuario', 'juego']
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.juego.titulo} ({self.cantidad})"
    
    @property
    def subtotal(self):
        return self.cantidad * self.juego.precio

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion_envio = models.TextField()
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-creado']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} ({self.estado})"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    juego = models.ForeignKey(Juego, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['pedido', 'juego']
    
    def __str__(self):
        return f"{self.pedido.id} - {self.juego.titulo} ({self.cantidad})"
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
