from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

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

    # Administración
    path("reportes/", include("apps.reportes.urls")),
    path("configuracion/", include("apps.configuracion.urls")),
    path("ayuda/", include("apps.ayuda.urls")),

    # Empleados
    path("empleados/", include("apps.empleados.urls")),

    #Dashboard
    path("dashboard/", include("apps.dashboard.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)