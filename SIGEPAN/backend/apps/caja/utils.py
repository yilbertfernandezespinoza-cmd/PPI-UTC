from decimal import Decimal

from .models import MovimientoCaja


# =====================================================
# CALCULAR SALDO DEL SISTEMA
# =====================================================

def calcular_saldo_sistema(apertura):

    movimientos = MovimientoCaja.objects.filter(
        apertura=apertura
    )

    saldo = apertura.monto_inicial

    for movimiento in movimientos:

        if movimiento.tipo_movimiento in [

            "VENTA",
            "INGRESO"

        ]:

            saldo += movimiento.monto

        elif movimiento.tipo_movimiento in [

            "RETIRO",
            "GASTO"

        ]:

            saldo -= movimiento.monto

        elif movimiento.tipo_movimiento == "AJUSTE":

            saldo += movimiento.monto

    return saldo

# =====================================================
# CALCULAR SALDO DE MOVIMIENTOS
# =====================================================

def calcular_saldo_movimientos(apertura):

    movimientos = MovimientoCaja.objects.filter(
        apertura=apertura
    )


    saldo = Decimal("0.00")


    for movimiento in movimientos:


        if movimiento.tipo_movimiento in [

            "VENTA",
            "INGRESO"

        ]:

            saldo += movimiento.monto


        elif movimiento.tipo_movimiento in [

            "RETIRO",
            "GASTO"

        ]:

            saldo -= movimiento.monto


        elif movimiento.tipo_movimiento == "AJUSTE":

            saldo += movimiento.monto


    return saldo