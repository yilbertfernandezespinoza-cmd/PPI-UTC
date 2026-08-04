// =====================================================
// SIGEPAN - Módulo: Ventas
// Archivo: venta_pos.js
// Descripción: Control de totales, resumen, generación de formsets de pago, búsqueda de clientes y gestión POS
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

    const formVenta = document.getElementById("form-pos-venta");
    const contenedorPagos = document.getElementById("contenedor_pagos_dinamicos");
    const contadorPagoDjango = document.getElementById("id_pago-TOTAL_FORMS");

    // Variable de control para saber si la acción actual es guardar como pendiente
    let esAccionPendiente = false;
    const btnGuardarPendiente = document.getElementById("btn_guardar_pendiente");
    if (btnGuardarPendiente) {
        btnGuardarPendiente.addEventListener("click", function() {
            esAccionPendiente = true;
        });
    }

    // ==========================================
    // 0. FUNCIÓN GLOBAL DE LIMPIEZA DE PANTALLA
    // ==========================================
    window.limpiarPantallaPOS = function() {
        if (formVenta) {
            formVenta.reset();
        }

        // Restablecer cliente predeterminado
        const clienteId = document.getElementById("cliente_id");
        const clienteSeleccionado = document.getElementById("cliente_seleccionado");
        if (clienteId) clienteId.value = "";
        if (clienteSeleccionado) clienteSeleccionado.innerText = "Público General";

        // Vaciar la tabla de productos / carrito
        const carritoProductos = document.getElementById("carrito_productos");
        if (carritoProductos) {
            carritoProductos.innerHTML = `
                <tr id="fila_vacia">
                    <td colspan="5" class="text-center text-muted py-5 pos-cart-empty">
                        <i class="bi bi-inbox fs-1 d-block mb-2 text-secondary opacity-50"></i>
                        No hay productos agregados a la venta
                    </td>
                </tr>
            `;
        }

        // Desmarcar checkboxes de pago y vaciar contenedor dinámico
        document.querySelectorAll(".metodo-pago-checkbox").forEach(cb => cb.checked = false);
        if (contenedorPagos) contenedorPagos.innerHTML = "";

        // Recalcular totales a cero
        if (typeof window.recalcularTotales === "function") {
            window.recalcularTotales();
        }
    };

    // ==========================================
    // 1. FUNCIÓN GLOBAL DE RECÁLCULO
    // ==========================================
    window.recalcularTotales = function() {
        let subtotalGeneral = 0;
        const inputsSubtotal = document.querySelectorAll(".input-subtotal-oculto");

        inputsSubtotal.forEach(function(input) {
            subtotalGeneral += parseFloat(input.value) || 0;
        });

        // Cálculo de IVA (13%)
        let iva = subtotalGeneral * 0.13;
        let descuento = 0; 
        let totalGeneral = subtotalGeneral + iva - descuento;

        // Actualizar interfaz visual
        const elSubtotal = document.getElementById("resumen_subtotal");
        const elIva = document.getElementById("resumen_iva");
        const elDescuento = document.getElementById("resumen_descuento");
        const elTotal = document.getElementById("resumen_total");

        if (elSubtotal) elSubtotal.innerText = `₡${subtotalGeneral.toFixed(2)}`;
        if (elIva) elIva.innerText = `₡${iva.toFixed(2)}`;
        if (elDescuento) elDescuento.innerText = `₡${descuento.toFixed(2)}`;
        if (elTotal) elTotal.innerText = `₡${totalGeneral.toFixed(2)}`;
    };

    // ==========================================
    // 2. SINCRONIZACIÓN DE PAGOS Y VALIDACIÓN PREVIA AL SUBMIT (COBRO)
    // ==========================================
    if (formVenta) {
        formVenta.addEventListener("submit", function(e) {
            const carrito = document.getElementById("carrito_productos");
            const filaVacia = document.getElementById("fila_vacia");

            // Validar carrito con productos
            if (!carrito || filaVacia || carrito.children.length === 0) {
                e.preventDefault();
                alert("Debe agregar al menos un producto al carrito antes de continuar.");
                esAccionPendiente = false; // Resetear bandera
                return;
            }

            // Detectar si el envío proviene del botón de guardar pendiente
            const submitter = e.submitter;
            const esPendientePorSubmitter = submitter && (
                submitter.id === "btn_guardar_pendiente" || 
                (submitter.getAttribute("formaction") && submitter.getAttribute("formaction").includes("pendiente"))
            );

            if (esAccionPendiente || esPendientePorSubmitter) {
                // Si es venta pendiente, no exigimos checkboxes de pago
                if (contenedorPagos) contenedorPagos.innerHTML = "";
                if (contadorPagoDjango) contadorPagoDjango.value = 0;
                esAccionPendiente = false; // Resetear bandera
                return; // Permitir el envío al backend
            }

            // Limpiar contenedor de pagos dinámicos previos
            if (contenedorPagos) contenedorPagos.innerHTML = "";

            // Capturar checkboxes de pago seleccionados para venta normal
            const checkboxesPago = document.querySelectorAll(".metodo-pago-checkbox:checked");

            if (checkboxesPago.length === 0) {
                e.preventDefault();
                alert("Debe seleccionar al menos un método de pago.");
                return;
            }

            // Obtener el total numérico actual de la venta
            const elTotalText = document.getElementById("resumen_total");
            let totalTexto = elTotalText ? elTotalText.innerText : "0";
            let totalNumerico = parseFloat(totalTexto.replace("₡", "").replace(/,/g, "")) || 0;

            // Actualizar TOTAL_FORMS del Formset de Pago de Django
            if (contadorPagoDjango) {
                contadorPagoDjango.value = checkboxesPago.length;
            }

            // DISTRIBUCIÓN EXACTA DE PAGOS (Blindaje contra errores de céntimos)
            let acumuladoAsignado = 0;

            checkboxesPago.forEach(function(checkbox, indice) {
                let metodo = checkbox.getAttribute("data-metodo");
                let montoAsignado;

                if (indice === checkboxesPago.length - 1) {
                    montoAsignado = totalNumerico - acumuladoAsignado;
                } else {
                    montoAsignado = Math.round((totalNumerico / checkboxesPago.length) * 100) / 100;
                    acumuladoAsignado += montoAsignado;
                }

                let htmlInputs = `
                    <input type="hidden" name="pago-${indice}-metodo_pago" value="${metodo}">
                    <input type="hidden" name="pago-${indice}-monto" value="${montoAsignado.toFixed(2)}">
                    <input type="hidden" name="pago-${indice}-referencia" value="POS-AUTOGENERADO">
                `;
                if (contenedorPagos) {
                    contenedorPagos.insertAdjacentHTML("beforeend", htmlInputs);
                }
            });
        });
    }

    // ==========================================
    // 3. BOTÓN: CANCELAR VENTA
    // ==========================================
    const btnCancelar = document.getElementById("btn_cancelar");
    if (btnCancelar) {
        btnCancelar.addEventListener("click", function(e) {
            e.preventDefault();

            if (confirm("¿Está seguro de que desea cancelar la venta actual? Se perderán los productos seleccionados.")) {
                window.limpiarPantallaPOS();
            }
        });
    }

    // ==========================================
    // 4. BÚSQUEDA Y SELECCIÓN DE CLIENTES (AJAX)
    // ==========================================
    const $inputBuscarCliente = $('#buscar_cliente');
    const $listaClientes = $('#lista_clientes_pos');
    const $clienteId = $('#cliente_id');
    const $clienteSeleccionado = $('#cliente_seleccionado');
    
    // Obtener la URL segura inyectada desde Django
    const configPos = document.getElementById('config-pos');
    const urlBuscarCliente = configPos ? $(configPos).data('url-buscar-cliente') : 'clientes/buscar/';

    function realizarBusquedaCliente(query) {
        if (query.trim().length === 0) {
            $listaClientes.html('').hide();
            return;
        }

        $.ajax({
            url: urlBuscarCliente,
            data: { 'q': query },
            dataType: 'json',
            success: function(data) {
                $listaClientes.html('');
                if (data.length > 0) {
                    data.forEach(function(cliente) {
                        $listaClientes.append(`
                            <a href="#" class="list-group-item list-group-item-action cliente-opcion py-2" 
                               data-id="${cliente.id_cliente || cliente.id}" 
                               data-nombre="${cliente.nombre}">
                                <div class="d-flex justify-content-between">
                                    <span class="fw-bold">${cliente.nombre}</span>
                                    <small class="text-muted">ID: ${cliente.identificacion || 'N/A'}</small>
                                </div>
                            </a>
                        `);
                    });
                    $listaClientes.show();
                } else {
                    $listaClientes.html(`
                        <div class="list-group-item text-muted py-2 small">
                            No se encontraron clientes
                        </div>
                    `).show();
                }
            },
            error: function(xhr) {
                console.error("Error al buscar clientes:", xhr.responseText);
            }
        });
    }

    if ($inputBuscarCliente.length) {
        // Evento al escribir
        $inputBuscarCliente.on('input', function() {
            realizarBusquedaCliente($(this).val());
        });

        // Evento al hacer clic en el botón de búsqueda
        $('#btn_buscar_cliente').on('click', function() {
            realizarBusquedaCliente($inputBuscarCliente.val());
        });

        // Seleccionar cliente de la lista
        $(document).on('click', '.cliente-opcion', function(e) {
            e.preventDefault();
            const idCliente = $(this).data('id');
            const nombreCliente = $(this).data('nombre');

            $clienteId.val(idCliente);
            $clienteSeleccionado.text(nombreCliente);

            $listaClientes.html('').hide();
            $inputBuscarCliente.val('');
        });

        // Ocultar lista al hacer clic fuera
        $(document).on('click', function(e) {
            if (!$(e.target).closest('#buscar_cliente, #lista_clientes_pos, #btn_buscar_cliente').length) {
                $listaClientes.hide();
            }
        });
    }

    // Ejecutar recálculo inicial (indispensable si se retomó una venta pendiente)
    if (typeof window.recalcularTotales === "function") {
        window.recalcularTotales();
    }
});