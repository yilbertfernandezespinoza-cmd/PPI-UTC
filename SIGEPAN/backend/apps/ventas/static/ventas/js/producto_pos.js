// =====================================================
// SIGEPAN - Módulo: Ventas
// Archivo: producto_pos.js
// Descripción: Búsqueda, selección y control del Formset de Detalles
// =====================================================

document.addEventListener("DOMContentLoaded", function() {

    // 1. CAPTURA DE ELEMENTOS DEL DOM
    const buscarProducto = document.getElementById("buscar_producto");
    const btnAgregar = document.getElementById("btn_agregar_producto");
    const carrito = document.getElementById("carrito_productos");
    const listaProductos = document.getElementById("lista_productos_pos");
    
    // Contador oficial de Django Formset
    const contadorDjango = document.getElementById("id_detalle-TOTAL_FORMS");

    if (!buscarProducto || !btnAgregar || !carrito || !contadorDjango || !listaProductos) {
        console.warn("Faltan elementos del DOM para inicializar producto_pos.js");
        return;
    }

    let productoSeleccionado = null;
    let timeoutBusqueda = null; // Para el debounce

    // 2. EVENTOS
    buscarProducto.addEventListener("keyup", function() {
        // Debounce: Esperar 300ms después de que el usuario deja de escribir para buscar
        clearTimeout(timeoutBusqueda);
        timeoutBusqueda = setTimeout(buscarProductos, 300);
    });

    btnAgregar.addEventListener("click", function() {
        if (!productoSeleccionado) {
            alert("Por favor, busque y seleccione un producto primero de la lista desplegable.");
            return;
        }
        agregarProducto(productoSeleccionado);
    });

    // Delegación de eventos para eliminar filas dinámicas y recalcular
    carrito.addEventListener("click", function(e) {
        let btnEliminar = e.target.closest(".btn-eliminar-fila");
        if (btnEliminar) {
            let fila = btnEliminar.closest("tr");
            fila.remove();
            
            // Reindexar formset después de eliminar
            reindexarFormsetDetalles();
            
            // Validar si la tabla quedó vacía para volver a mostrar el mensaje
            if (carrito.children.length === 0) {
                carrito.innerHTML = `
                    <tr id="fila_vacia">
                        <td colspan="5" class="text-center text-muted py-5 pos-cart-empty">
                            <i class="bi bi-inbox fs-1 d-block mb-2 text-secondary opacity-50"></i>
                            No hay productos agregados a la venta
                        </td>
                    </tr>
                `;
            }
            
            // Disparar recálculo global
            if (typeof window.recalcularTotales === "function") {
                window.recalcularTotales();
            }
        }
    });

    // Delegación de eventos para recalcular si cambia la cantidad (input dinámico)
    carrito.addEventListener("change", function(e) {
        if (e.target.classList.contains("input-cantidad-pos")) {
            let fila = e.target.closest("tr");
            let cantidad = parseFloat(e.target.value) || 1;
            
            if (cantidad < 1) {
                cantidad = 1;
                e.target.value = 1;
            }

            let precioUnitarioInput = fila.querySelector(".input-precio-unitario");
            let precio = parseFloat(precioUnitarioInput.value) || 0;
            
            let nuevoSubtotal = cantidad * precio;
            
            // Actualizar visual y oculto
            fila.querySelector(".celda-subtotal-visual").innerText = `₡${nuevoSubtotal.toFixed(2)}`;
            fila.querySelector(".input-subtotal-oculto").value = nuevoSubtotal.toFixed(2);
            
            // Disparar recálculo global
            if (typeof window.recalcularTotales === "function") {
                window.recalcularTotales();
            }
        }
    });

    // 3. FUNCIONES LÓGICAS
    async function buscarProductos() {
        let texto = buscarProducto.value.trim();

        if (texto.length < 2) {
            listaProductos.innerHTML = "";
            listaProductos.classList.add("d-none");
            productoSeleccionado = null;
            return;
        }

        try {
            const respuesta = await fetch(`/productos/pos/buscar/?q=${encodeURIComponent(texto)}`);
            const productos = await respuesta.json();
            mostrarResultados(productos);
        } catch (error) {
            console.error("Error buscando productos en SIGEPAN:", error);
        }
    }

    function mostrarResultados(productos) {
        listaProductos.innerHTML = "";

        if (productos.length === 0) {
            listaProductos.innerHTML = `
                <div class="list-group-item text-muted">
                    No se encontraron productos
                </div>
            `;
            listaProductos.classList.remove("d-none");
            return;
        }

        productos.forEach(function(producto) {
            let item = document.createElement("button");
            item.type = "button";
            item.className = "list-group-item list-group-item-action";
            item.innerHTML = `
                <strong>${producto.nombre}</strong><br>
                <small>Código: ${producto.codigo} | Precio: ₡${parseFloat(producto.precio).toFixed(2)}</small>
            `;

            item.addEventListener("click", function() {
                productoSeleccionado = producto;
                buscarProducto.value = producto.nombre;
                listaProductos.innerHTML = "";
                listaProductos.classList.add("d-none");
            });

            listaProductos.appendChild(item);
        });

        listaProductos.classList.remove("d-none");
    }

    // =====================================================
    // FUNCIÓN DE REINDEXACIÓN PARA DJANGO FORMSET
    // =====================================================
    function reindexarFormsetDetalles() {
        const filas = carrito.querySelectorAll("tr:not(#fila_vacia)");
        filas.forEach((fila, nuevoIndice) => {
            const inputs = fila.querySelectorAll("input");
            inputs.forEach(input => {
                input.name = input.name.replace(/detalle-\d+/, `detalle-${nuevoIndice}`);
            });
        });
        if (contadorDjango) {
            contadorDjango.value = filas.length;
        }
    }

    // =====================================================
    // FUNCIÓN AGREGAR PRODUCTO AL CARRITO
    // =====================================================
    function agregarProducto(producto) {
        let filaVacia = document.getElementById("fila_vacia");
        if (filaVacia) {
            filaVacia.remove();
        }

        let cantidad = 1;
        let precio = parseFloat(producto.precio);
        let subtotal = precio * cantidad;
        
        // Obtener el índice actual basado en el contador
        let indice = parseInt(contadorDjango.value) || 0;

        let fila = document.createElement("tr");
        fila.innerHTML = `
            <td class="align-middle">
                ${producto.nombre}
                <input type="hidden" name="detalle-${indice}-producto" value="${producto.id}">
            </td>
            <td class="align-middle text-center">
                <input class="form-control form-control-sm text-center mx-auto input-cantidad-pos" style="width: 80px;" type="number" name="detalle-${indice}-cantidad" value="${cantidad}" min="1" step="1">
            </td>
            <td class="align-middle text-end">
                ₡${precio.toFixed(2)}
                <input type="hidden" class="input-precio-unitario" name="detalle-${indice}-precio_unitario" value="${precio.toFixed(2)}">
            </td>
            <td class="align-middle text-end fw-bold celda-subtotal-visual">
                ₡${subtotal.toFixed(2)}
            </td>
            <td class="align-middle text-center">
                <input type="hidden" class="input-subtotal-oculto" name="detalle-${indice}-subtotal" value="${subtotal.toFixed(2)}">
                <button type="button" class="btn btn-danger btn-sm btn-eliminar-fila">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;

        carrito.appendChild(fila);

        // Reindexar y actualizar el contador de Django
        reindexarFormsetDetalles();

        // Limpiar búsqueda
        buscarProducto.value = "";
        productoSeleccionado = null;
        buscarProducto.focus();

        // Disparar recálculo global de totales
        if (typeof window.recalcularTotales === "function") {
            window.recalcularTotales();
        }
    }
});