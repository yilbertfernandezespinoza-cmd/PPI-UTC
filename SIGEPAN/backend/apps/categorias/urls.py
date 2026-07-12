from django.urls import path
from . import views

app_name = "categorias"

urlpatterns = [
    path('', views.lista_categorias, name='lista_categorias'),
    path('nueva/', views.nueva_categoria, name='nueva_categoria'),
    path('editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    
]

