from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages


from .models import Inventario


from .forms import InventarioForm




# =====================================================
# LISTA DE INVENTARIO
# =====================================================

def lista_inventario(request):


    inventarios = Inventario.objects.all().order_by(

        "producto__nombre"

    )



    return render(

        request,

        "inventario/lista_inventario.html",

        {

            "inventarios": inventarios

        }

    )





# =====================================================
# DETALLE INVENTARIO
# =====================================================

def detalle_inventario(request, id_inventario):


    inventario = get_object_or_404(

        Inventario,

        id_inventario=id_inventario

    )



    return render(

        request,

        "inventario/detalle_inventario.html",

        {

            "inventario": inventario

        }

    )





# =====================================================
# EDITAR CONFIGURACION INVENTARIO
# =====================================================

def editar_inventario(request, id_inventario):


    inventario = get_object_or_404(

        Inventario,

        id_inventario=id_inventario

    )



    if request.method == "POST":


        form = InventarioForm(

            request.POST,

            instance=inventario

        )



        if form.is_valid():


            form.save()



            messages.success(

                request,

                "Inventario actualizado correctamente."

            )


            return redirect(

                "inventario:lista_inventario"

            )



    else:


        form = InventarioForm(

            instance=inventario

        )



    return render(

        request,

        "inventario/editar_inventario.html",

        {

            "form": form,

            "inventario": inventario

        }

    )