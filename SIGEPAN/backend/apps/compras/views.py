from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError


from .models import (
    Compra,
    DetalleCompra
)


from .forms import (
    CompraForm,
    DetalleCompraFormSet
)


from apps.security.models import Usuario

from apps.inventario.models import TipoMovimientoInventario
from apps.inventario.repositories import InventarioRepository
from apps.inventario.services import MovimientoInventarioService





# =====================================================
# LISTAR COMPRAS
# =====================================================

def lista_compras(request):

    compras = Compra.objects.all().order_by(
        "-fecha"
    )

    return render(

        request,

        "compras/lista_compras.html",

        {
            "compras": compras
        }

    )





# =====================================================
# CREAR COMPRA
# =====================================================

@transaction.atomic
def crear_compra(request):


    usuario_id = request.session.get(
        "usuario_id"
    )


    usuario_actual = get_object_or_404(

        Usuario,

        id_usuario=usuario_id

    )



    if request.method == "POST":


        compra_form = CompraForm(
            request.POST
        )


        detalle_formset = DetalleCompraFormSet(

            request.POST

        )



        if compra_form.is_valid() and detalle_formset.is_valid():

            # Tipo de movimiento requerido para poder registrar la entrada
            # de inventario. Se valida antes de guardar nada de la compra
            # para no dejarla a medias si todavía no se sembró el catálogo.
            try:
                tipo_entrada_compra = TipoMovimientoInventario.objects.get(
                    nombre="ENTRADA_COMPRA"
                )
            except TipoMovimientoInventario.DoesNotExist:
                messages.error(
                    request,
                    "Falta configurar el tipo de movimiento 'ENTRADA_COMPRA' en "
                    "Inventario. Ejecute: python manage.py seed_tipos_movimiento"
                )
                return redirect("compras:crear_compra")

            compra = compra_form.save(
                commit=False
            )



            # ==========================================
            # DATOS AUTOMATICOS
            # ==========================================

            compra.usuario = usuario_actual

            compra.fecha = timezone.now()

            compra.estado = True



            # Inicialmente en cero,
            # luego se calcula

            compra.total = 0



            compra.save()



            detalles = detalle_formset.save(
                commit=False
            )



            total_compra = 0



            for detalle in detalles:



                detalle.compra = compra



                detalle.subtotal = (

                    detalle.cantidad *

                    detalle.precio_unitario

                )



                total_compra += detalle.subtotal



                detalle.save()



                # ======================================
                # ACTUALIZAR INVENTARIO (vía
                # MovimientoInventarioService: crea el registro de
                # inventario si todavía no existe para ese producto+sucursal
                # -antes se omitía en silencio- y deja rastro en
                # movimiento_inventario en vez de mutar stock_actual a mano)
                # ======================================

                inventario = InventarioRepository.obtener_o_crear(
                    detalle.producto, usuario_actual.id_sucursal
                )

                try:
                    MovimientoInventarioService.registrar_movimiento(
                        inventario=inventario,
                        tipo_movimiento=tipo_entrada_compra,
                        usuario=usuario_actual,
                        cantidad=detalle.cantidad,
                        observaciones=f"Compra #{compra.id_compra}",
                    )
                except ValidationError as error:
                    transaction.set_rollback(True)
                    messages.error(
                        request,
                        f"{detalle.producto.nombre}: {'; '.join(error.messages) if hasattr(error, 'messages') else error}"
                    )
                    return redirect("compras:crear_compra")



            # ==========================================
            # ACTUALIZAR TOTAL FINAL
            # ==========================================

            compra.total = total_compra

            compra.save(
                update_fields=[
                    "total"
                ]
            )



            messages.success(

                request,

                "Compra registrada correctamente."

            )


            return redirect(

                "compras:detalle_compra",

                id_compra=compra.id_compra

            )



    else:


        compra_form = CompraForm()


        detalle_formset = DetalleCompraFormSet()



    return render(

        request,

        "compras/crear_compra.html",

        {

            "compra_form": compra_form,

            "detalle_formset": detalle_formset

        }

    )






# =====================================================
# DETALLE DE COMPRA
# =====================================================

def detalle_compra(request, id_compra):


    compra = get_object_or_404(

        Compra,

        id_compra=id_compra

    )


    detalles = DetalleCompra.objects.filter(

        compra=compra

    )


    return render(

        request,

        "compras/detalle_compra.html",

        {

            "compra": compra,

            "detalles": detalles

        }

    )






# =====================================================
# ANULAR COMPRA
# =====================================================

@transaction.atomic
def anular_compra(request, id_compra):


    compra = get_object_or_404(

        Compra,

        id_compra=id_compra

    )



    if request.method == "POST":


        if compra.estado:


            detalles = DetalleCompra.objects.filter(

                compra=compra

            )



            usuario_id = request.session.get(

                "usuario_id"

            )


            usuario_actual = get_object_or_404(

                Usuario,

                id_usuario=usuario_id

            )

            try:
                tipo_devolucion_compra = TipoMovimientoInventario.objects.get(
                    nombre="DEVOLUCION_COMPRA"
                )
            except TipoMovimientoInventario.DoesNotExist:
                messages.error(
                    request,
                    "Falta configurar el tipo de movimiento 'DEVOLUCION_COMPRA' "
                    "en Inventario. Ejecute: python manage.py seed_tipos_movimiento"
                )
                return redirect("compras:lista_compras")



            # ======================================
            # DEVOLVER INVENTARIO (vía MovimientoInventarioService)
            # ======================================


            for detalle in detalles:


                inventario = InventarioRepository.obtener_para_actualizar(
                    detalle.producto, usuario_actual.id_sucursal
                )

                if not inventario:
                    messages.warning(
                        request,
                        f"No se encontró inventario de {detalle.producto.nombre} "
                        f"en la sucursal actual; no se pudo revertir el stock de "
                        f"esa línea."
                    )
                    continue

                try:
                    MovimientoInventarioService.registrar_movimiento(
                        inventario=inventario,
                        tipo_movimiento=tipo_devolucion_compra,
                        usuario=usuario_actual,
                        cantidad=detalle.cantidad,
                        observaciones=f"Anulación de compra #{compra.id_compra}",
                    )
                except ValidationError as error:
                    transaction.set_rollback(True)
                    messages.error(
                        request,
                        f"{detalle.producto.nombre}: {'; '.join(error.messages) if hasattr(error, 'messages') else error}"
                    )
                    return redirect("compras:lista_compras")



            compra.estado = False


            compra.save()



        messages.success(

            request,

            "Compra anulada correctamente."

        )


        return redirect(

            "compras:lista_compras"

        )



    return render(

        request,

        "compras/anular_compra.html",

        {

            "compra": compra

        }

    )