from django.urls import path
from . import views

app_name = "categorias"

urlpatterns = [
    path('', views.lista_categorias, name='lista_categorias'),
    path('nueva/', views.nueva_categoria, name='nueva_categoria'),
    path('editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('estado/<int:pk>/', views.cambiar_estado_categoria, name='cambiar_estado_categoria'),
    
]

