"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # Core
    path("",include("apps.core.urls")),

    # Seguridad
    path("security/", include("apps.security.urls")),

    # Catálogos
    path("productos/", include("apps.productos.urls")),
    path("categorias/", include("apps.categorias.urls")),
    path("clientes/", include("apps.clientes.urls")),
    path("proveedores/", include("apps.proveedores.urls")),

    # Operaciones
    path("inventario/", include("apps.inventario.urls")),
    path("compras/", include("apps.compras.urls")),
    path("ventas/", include("apps.ventas.urls")),
    path("caja/", include("apps.caja.urls")),
    path("mermas/", include("apps.mermas.urls")),
    path("ajustes/", include("apps.ajustes.urls")),
    path("gastos-operativos/", include("apps.gastos_operativos.urls")),

    # Administración
    path("reportes/", include("apps.reportes.urls")),
    path("configuracion/", include("apps.configuracion.urls")),
    path("ayuda/", include("apps.ayuda.urls")),

    # Empleados
    path("empleados/", include("apps.empleados.urls")),

    #Dashboard
    path("dashboard/", include("apps.dashboard.urls")),

]
