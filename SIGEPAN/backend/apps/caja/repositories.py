# Repositorios del módulo

from django.shortcuts import get_object_or_404

from .models import (
    Caja,
    HistorialCaja,
    AperturaCaja,
    MovimientoCaja,
    ArqueoCaja,
)


# =====================================================
# CAJA
# =====================================================

class CajaRepository:
    """
    Acceso a datos de Caja (RF-014/015).

    Agregado 07-08 (hallazgo de auditoría): antes todas las consultas ORM
    de Caja/AperturaCaja/MovimientoCaja/ArqueoCaja/HistorialCaja vivían
    directo en views.py, sin capa Repository — a diferencia de
    Ventas/Inventario/Mermas/Ajustes/Compras/Gastos Operativos, que sí la
    tienen. Se extraen aquí exactamente las mismas consultas (mismos
    filtros, mismo orden) que ya existían en las vistas, sin cambiar
    comportamiento.
    """

    @staticmethod
    def listar_todas():
        return Caja.objects.all()

    @staticmethod
    def obtener(id_caja):
        return get_object_or_404(Caja, id_caja=id_caja)

    @staticmethod
    def apertura_activa(caja):
        """Apertura activa de una caja, o None si está cerrada."""
        return AperturaCaja.objects.filter(caja=caja, estado=True).first()

    @staticmethod
    def tiene_apertura_activa(caja):
        return AperturaCaja.objects.filter(caja=caja, estado=True).exists()


# =====================================================
# APERTURA DE CAJA
# =====================================================

class AperturaCajaRepository:

    @staticmethod
    def obtener(id_apertura):
        return get_object_or_404(AperturaCaja, id_apertura=id_apertura)


# =====================================================
# MOVIMIENTOS DE CAJA
# =====================================================

class MovimientoCajaRepository:

    @staticmethod
    def listar_por_apertura(apertura):
        return MovimientoCaja.objects.filter(
            apertura=apertura
        ).order_by("-fecha_movimiento")

    @staticmethod
    def recientes(apertura, limite=10):
        return MovimientoCajaRepository.listar_por_apertura(apertura)[:limite]

    @staticmethod
    def contar(apertura):
        return MovimientoCaja.objects.filter(apertura=apertura).count()


# =====================================================
# ARQUEOS DE CAJA
# =====================================================

class ArqueoCajaRepository:

    @staticmethod
    def listar_por_apertura(apertura):
        return ArqueoCaja.objects.filter(
            apertura=apertura
        ).order_by("-fecha_arqueo")

    @staticmethod
    def ultimo(apertura):
        return ArqueoCajaRepository.listar_por_apertura(apertura).first()

    @staticmethod
    def existe_para_apertura(apertura):
        return ArqueoCaja.objects.filter(apertura=apertura).exists()


# =====================================================
# HISTORIAL ADMINISTRATIVO DE CAJA
# =====================================================

class HistorialCajaRepository:

    @staticmethod
    def listar_por_caja(caja):
        return HistorialCaja.objects.filter(
            caja=caja
        ).order_by("-fecha_creacion")

    @staticmethod
    def registrar(caja, usuario, tipo_cambio, valor_anterior, valor_nuevo, observacion):
        return HistorialCaja.objects.create(
            caja=caja,
            usuario=usuario,
            tipo_cambio=tipo_cambio,
            valor_anterior=str(valor_anterior),
            valor_nuevo=str(valor_nuevo),
            observacion=observacion,
        )
