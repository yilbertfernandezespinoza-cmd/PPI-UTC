// =====================================================
// SIGEPAN - Módulo: Ventas
// Archivo: venta_pos.js
// Descripción: Lógica completa del POS (carrito, cuadrícula de
//              categorías/productos, búsqueda de clientes, cobro y pausa).
// =====================================================
//
// Este archivo reemplaza a producto_pos.js + venta_pos.js. Hasta el
// 04-08-2026 el carrito del POS se armaba con inputs ocultos indexados
// ("detalle-0-producto", "detalle-0-cantidad", ...) para calzar con un
// Django inlineformset_factory. Ese enfoque generó tres rondas de bugs
// (método de pago con texto en vez de PK real, reanudar sin repoblar el
// carrito, y finalmente "id_detalle_venta: Este campo es obligatorio" al
// pausar una venta) y se abandonó por completo.
//
// Ahora el carrito es un único array de JavaScript (fuente de verdad) que
// se renderiza en la tabla #carrito_productos y se envía completo como
// JSON a apps.ventas.views.procesar_venta vía fetch(). El servidor vuelve
// a calcular precios/impuesto/total desde Producto.precio_venta: los
// totales que se muestran aquí son solo un estimado visual para el
// cajero, nunca la fuente de verdad del dinero.

document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // 0. ELEMENTOS DEL DOM Y CONFIGURACIÓN
    // =====================================================
    const configPos = document.getElementById("config-pos");
    if (!configPos) {
        console.warn("No se encontró #config-pos: el POS no puede inicializarse.");
        return;
    }

    const urlBuscarCliente = configPos.dataset.urlBuscarCliente;
    const urlBuscarProducto = configPos.dataset.urlBuscarProducto;
    const urlProcesarVenta = configPos.dataset.urlProcesarVenta;

    const carritoTbody = document.getElementById("carrito_productos");
    const buscarProductoInput = document.getElementById("buscar_producto");
    const listaProductosPos = document.getElementById("lista_productos_pos");
    const contenedorCategorias = document.getElementById("pos_categorias");
    const gridProductos = document.getElementById("pos_productos_grid");

    const buscarClienteInput = document.getElementById("buscar_cliente");
    const btnBuscarCliente = document.getElementById("btn_buscar_cliente");
    const listaClientesPos = document.getElementById("lista_clientes_pos");
    const clienteIdInput = document.getElementById("cliente_id");
    const clienteSeleccionadoSpan = document.getElementById("cliente_seleccionado");

    const btnCobrar = document.getElementById("btn_cobrar");
    const btnGuardarPendiente = document.getElementById("btn_guardar_pendiente");
    const btnCancelar = document.getElementById("btn_cancelar");
    const posAlertas = document.getElementById("pos_alertas");

    // =====================================================
    // 1. ESTADO: EL CARRITO (fuente de verdad única)
    // =====================================================
    // Cada línea: { producto_id, nombre, precio, cantidad, subtotal }
    let carrito = [];

    // =====================================================
    // 2. UTILIDADES
    // =====================================================
    function getCsrfToken() {
        const input = document.querySelector("input[name=csrfmiddlewaretoken]");
        return input ? input.value : "";
    }

    function formatoMoneda(valor) {
        return "₡" + (parseFloat(valor) || 0).toFixed(2);
    }

    function mostrarAlerta(mensaje, tipo) {
        tipo = tipo || "danger";
        if (!posAlertas) {
            alert(mensaje);
            return;
        }
        posAlertas.innerHTML = `
            <div class="alert alert-${tipo} alert-dismissible fade show shadow-sm" role="alert">
                ${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        posAlertas.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function limpiarAlertas() {
        if (posAlertas) posAlertas.innerHTML = "";
    }

    // =====================================================
    // 3. RENDER DEL CARRITO (a partir del array, nunca al revés)
    // =====================================================
    function renderizarCarrito() {
        if (!carritoTbody) return;

        if (carrito.length === 0) {
            carritoTbody.innerHTML = `
                <tr id="fila_vacia">
                    <td colspan="5" class="text-center text-muted py-5 pos-cart-empty">
                        <i class="bi bi-inbox fs-1 d-block mb-2 text-secondary opacity-50"></i>
                        No hay productos agregados a la venta
                    </td>
                </tr>
            `;
            recalcularTotales();
            return;
        }

        carritoTbody.innerHTML = carrito.map(function (linea, indice) {
            const subtotal = linea.precio * linea.cantidad;
            return `
                <tr data-indice="${indice}">
                    <td class="align-middle">${linea.nombre}</td>
                    <td class="align-middle text-center">
                        <input
                            class="form-control form-control-sm text-center mx-auto input-cantidad-pos"
                            style="width: 80px;"
                            type="number"
                            min="1"
                            step="1"
                            value="${linea.cantidad}"
                            data-indice="${indice}"
                        >
                    </td>
                    <td class="align-middle text-end">${formatoMoneda(linea.precio)}</td>
                    <td class="align-middle text-end fw-bold">${formatoMoneda(subtotal)}</td>
                    <td class="align-middle text-center">
                        <button type="button" class="btn btn-danger btn-sm btn-eliminar-fila" data-indice="${indice}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join("");

        recalcularTotales();
    }

    // Delegación de eventos: cambiar cantidad
    if (carritoTbody) {
        carritoTbody.addEventListener("change", function (e) {
            if (!e.target.classList.contains("input-cantidad-pos")) return;

            const indice = parseInt(e.target.dataset.indice, 10);
            let cantidad = parseInt(e.target.value, 10);

            if (!cantidad || cantidad < 1) {
                cantidad = 1;
            }

            if (carrito[indice]) {
                carrito[indice].cantidad = cantidad;
            }

            renderizarCarrito();
        });

        // Delegación de eventos: eliminar fila
        carritoTbody.addEventListener("click", function (e) {
            const btn = e.target.closest(".btn-eliminar-fila");
            if (!btn) return;

            const indice = parseInt(btn.dataset.indice, 10);
            carrito.splice(indice, 1);
            renderizarCarrito();
        });
    }

    // =====================================================
    // 4. AGREGAR PRODUCTO AL CARRITO
    // =====================================================
    // Usada tanto por los tiles de la cuadrícula de categorías como por el
    // buscador de texto y por el repoblado de una venta pausada. Si el
    // producto ya está en el carrito, solo suma la cantidad en vez de
    // crear una fila duplicada.
    function agregarProductoAlCarrito(producto, cantidad) {
        cantidad = cantidad || 1;

        const productoId = parseInt(producto.id ?? producto.producto_id, 10);
        const precio = parseFloat(producto.precio ?? producto.precio_venta ?? 0);
        const nombre = producto.nombre;

        const existente = carrito.find(function (linea) {
            return linea.producto_id === productoId;
        });

        if (existente) {
            existente.cantidad += cantidad;
        } else {
            carrito.push({
                producto_id: productoId,
                nombre: nombre,
                precio: precio,
                cantidad: cantidad,
            });
        }

        renderizarCarrito();
    }

    // =====================================================
    // 5. RECALCULAR TOTALES (SOLO PREVIEW VISUAL)
    // =====================================================
    // El total real (incluyendo impuesto, que depende de la configuración
    // tributaria activa) siempre lo calcula el servidor en procesar_venta.
    // Aquí se usa una tasa de IVA fija (13%) únicamente para que el cajero
    // vea un estimado mientras arma el carrito.
    window.recalcularTotales = function () {
        const subtotal = carrito.reduce(function (acumulado, linea) {
            return acumulado + (linea.precio * linea.cantidad);
        }, 0);

        const iva = subtotal * 0.13;
        const descuento = 0;
        const total = subtotal + iva - descuento;

        const elSubtotal = document.getElementById("resumen_subtotal");
        const elIva = document.getElementById("resumen_iva");
        const elDescuento = document.getElementById("resumen_descuento");
        const elTotal = document.getElementById("resumen_total");

        if (elSubtotal) elSubtotal.innerText = formatoMoneda(subtotal);
        if (elIva) elIva.innerText = formatoMoneda(iva);
        if (elDescuento) elDescuento.innerText = formatoMoneda(descuento);
        if (elTotal) elTotal.innerText = formatoMoneda(total);
    };

    function recalcularTotales() {
        window.recalcularTotales();
    }

    // =====================================================
    // 6. BUSCADOR DE TEXTO DE PRODUCTOS (debounce + AJAX)
    // =====================================================
    let timeoutBusquedaProducto = null;

    if (buscarProductoInput) {
        buscarProductoInput.addEventListener("keyup", function () {
            clearTimeout(timeoutBusquedaProducto);
            timeoutBusquedaProducto = setTimeout(buscarProductosPorTexto, 300);
        });

        document.addEventListener("click", function (e) {
            if (!e.target.closest("#buscar_producto, #lista_productos_pos")) {
                listaProductosPos.classList.add("d-none");
            }
        });
    }

    async function buscarProductosPorTexto() {
        const texto = buscarProductoInput.value.trim();

        if (texto.length < 2) {
            listaProductosPos.innerHTML = "";
            listaProductosPos.classList.add("d-none");
            return;
        }

        try {
            const respuesta = await fetch(`${urlBuscarProducto}?q=${encodeURIComponent(texto)}`);
            const productos = await respuesta.json();
            mostrarResultadosBusquedaProducto(productos);
        } catch (error) {
            console.error("Error buscando productos en SIGEPAN:", error);
        }
    }

    function mostrarResultadosBusquedaProducto(productos) {
        listaProductosPos.innerHTML = "";

        if (productos.length === 0) {
            listaProductosPos.innerHTML = `
                <div class="list-group-item text-muted">No se encontraron productos</div>
            `;
            listaProductosPos.classList.remove("d-none");
            return;
        }

        productos.forEach(function (producto) {
            const item = document.createElement("button");
            item.type = "button";
            item.className = "list-group-item list-group-item-action";
            item.innerHTML = `
                <strong>${producto.nombre}</strong><br>
                <small>Código: ${producto.codigo} | Precio: ${formatoMoneda(producto.precio)}</small>
            `;

            item.addEventListener("click", function () {
                agregarProductoAlCarrito(producto, 1);
                buscarProductoInput.value = "";
                listaProductosPos.innerHTML = "";
                listaProductosPos.classList.add("d-none");
                buscarProductoInput.focus();
            });

            listaProductosPos.appendChild(item);
        });

        listaProductosPos.classList.remove("d-none");
    }

    // =====================================================
    // 7. CUADRÍCULA DE CATEGORÍAS + PRODUCTOS (tiles táctiles)
    // =====================================================
    if (contenedorCategorias) {
        contenedorCategorias.addEventListener("click", async function (e) {
            const boton = e.target.closest(".pos-category-btn");
            if (!boton) return;

            contenedorCategorias.querySelectorAll(".pos-category-btn").forEach(function (b) {
                b.classList.remove("active");
            });
            boton.classList.add("active");

            const categoriaId = boton.dataset.categoriaId;
            await cargarProductosPorCategoria(categoriaId);
        });
    }

    async function cargarProductosPorCategoria(categoriaId) {
        gridProductos.innerHTML = `
            <p class="text-muted small mb-0"><i class="bi bi-hourglass-split me-1"></i> Cargando productos...</p>
        `;

        try {
            const respuesta = await fetch(`${urlBuscarProducto}?categoria_id=${encodeURIComponent(categoriaId)}`);
            const productos = await respuesta.json();
            renderizarGridProductos(productos);
        } catch (error) {
            console.error("Error cargando productos por categoría en SIGEPAN:", error);
            gridProductos.innerHTML = `
                <p class="text-danger small mb-0">No se pudieron cargar los productos de esta categoría.</p>
            `;
        }
    }

    function renderizarGridProductos(productos) {
        if (!productos || productos.length === 0) {
            gridProductos.innerHTML = `
                <p class="text-muted small mb-0">Esta categoría no tiene productos activos.</p>
            `;
            return;
        }

        gridProductos.innerHTML = "";

        productos.forEach(function (producto) {
            const tile = document.createElement("button");
            tile.type = "button";
            tile.className = "pos-product-tile";
            tile.innerHTML = `
                <span class="pos-product-tile-nombre">${producto.nombre}</span>
                <span class="pos-product-tile-precio">${formatoMoneda(producto.precio)}</span>
            `;

            tile.addEventListener("click", function () {
                agregarProductoAlCarrito(producto, 1);

                // Feedback visual inmediato: el tile "destella" al agregarse.
                tile.classList.add("pos-product-tile-added");
                setTimeout(function () {
                    tile.classList.remove("pos-product-tile-added");
                }, 250);
            });

            gridProductos.appendChild(tile);
        });
    }

    // =====================================================
    // 8. BÚSQUEDA Y SELECCIÓN DE CLIENTES (AJAX)
    // =====================================================
    let timeoutBusquedaCliente = null;

    function realizarBusquedaCliente(query) {
        if (!query || query.trim().length === 0) {
            listaClientesPos.innerHTML = "";
            listaClientesPos.classList.add("d-none");
            return;
        }

        fetch(`${urlBuscarCliente}?q=${encodeURIComponent(query)}`)
            .then(function (respuesta) { return respuesta.json(); })
            .then(function (data) {
                listaClientesPos.innerHTML = "";

                if (data.length > 0) {
                    data.forEach(function (cliente) {
                        const item = document.createElement("a");
                        item.href = "#";
                        item.className = "list-group-item list-group-item-action cliente-opcion py-2";
                        item.dataset.id = cliente.id;
                        item.dataset.nombre = cliente.nombre;
                        item.innerHTML = `
                            <div class="d-flex justify-content-between">
                                <span class="fw-bold">${cliente.nombre}</span>
                                <small class="text-muted">ID: ${cliente.identificacion || "N/A"}</small>
                            </div>
                        `;
                        listaClientesPos.appendChild(item);
                    });
                } else {
                    listaClientesPos.innerHTML = `
                        <div class="list-group-item text-muted py-2 small">No se encontraron clientes</div>
                    `;
                }

                listaClientesPos.classList.remove("d-none");
            })
            .catch(function (error) {
                console.error("Error al buscar clientes:", error);
            });
    }

    if (buscarClienteInput) {
        buscarClienteInput.addEventListener("input", function () {
            clearTimeout(timeoutBusquedaCliente);
            const valor = this.value;
            timeoutBusquedaCliente = setTimeout(function () {
                realizarBusquedaCliente(valor);
            }, 300);
        });
    }

    if (btnBuscarCliente) {
        btnBuscarCliente.addEventListener("click", function () {
            realizarBusquedaCliente(buscarClienteInput.value);
        });
    }

    if (listaClientesPos) {
        listaClientesPos.addEventListener("click", function (e) {
            const opcion = e.target.closest(".cliente-opcion");
            if (!opcion) return;

            e.preventDefault();
            clienteIdInput.value = opcion.dataset.id;
            clienteSeleccionadoSpan.textContent = opcion.dataset.nombre;
            listaClientesPos.innerHTML = "";
            listaClientesPos.classList.add("d-none");
            buscarClienteInput.value = "";
        });

        document.addEventListener("click", function (e) {
            if (!e.target.closest("#buscar_cliente, #lista_clientes_pos, #btn_buscar_cliente")) {
                listaClientesPos.classList.add("d-none");
            }
        });
    }

    function limpiarCliente() {
        clienteIdInput.value = "";
        clienteSeleccionadoSpan.textContent = "Público General";
    }

    // =====================================================
    // 9. DISTRIBUCIÓN DE PAGOS (según checkboxes marcados)
    // =====================================================
    // Reparte el total estimado entre los métodos de pago seleccionados en
    // partes iguales (con la diferencia de céntimos absorbida por el
    // último), igual que el flujo anterior. Es solo una propuesta inicial:
    // el servidor únicamente exige que la SUMA de los pagos cubra el total
    // real que él mismo calcula.
    function construirPagosDesdeCheckboxes(totalEstimado) {
        const checkboxes = document.querySelectorAll(".metodo-pago-checkbox:checked");
        const pagos = [];
        let acumulado = 0;

        checkboxes.forEach(function (checkbox, indice) {
            let monto;
            if (indice === checkboxes.length - 1) {
                monto = totalEstimado - acumulado;
            } else {
                monto = Math.round((totalEstimado / checkboxes.length) * 100) / 100;
                acumulado += monto;
            }

            pagos.push({
                metodo_pago_id: parseInt(checkbox.dataset.metodo, 10),
                monto: monto.toFixed(2),
                referencia: "",
            });
        });

        return pagos;
    }

    function obtenerTotalEstimado() {
        const elTotal = document.getElementById("resumen_total");
        const texto = elTotal ? elTotal.innerText : "0";
        return parseFloat(texto.replace("₡", "").replace(/,/g, "")) || 0;
    }

    // =====================================================
    // 10. ENVÍO A procesar_venta() (JSON/AJAX)
    // =====================================================
    async function enviarVenta(accion) {
        if (carrito.length === 0) {
            mostrarAlerta("Debe agregar al menos un producto al carrito antes de continuar.");
            return;
        }

        const payload = {
            accion: accion,
            cliente_id: clienteIdInput.value ? parseInt(clienteIdInput.value, 10) : null,
            tipo_comprobante: "TICKET",
            productos: carrito.map(function (linea) {
                return {
                    producto_id: linea.producto_id,
                    cantidad: linea.cantidad,
                };
            }),
        };

        if (accion === "cobrar") {
            const checkboxes = document.querySelectorAll(".metodo-pago-checkbox:checked");
            if (checkboxes.length === 0) {
                mostrarAlerta("Debe seleccionar al menos un método de pago.");
                return;
            }
            payload.pagos = construirPagosDesdeCheckboxes(obtenerTotalEstimado());
        }

        const botones = [btnCobrar, btnGuardarPendiente].filter(Boolean);
        botones.forEach(function (b) { b.disabled = true; });
        limpiarAlertas();

        try {
            const respuesta = await fetch(urlProcesarVenta, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify(payload),
            });

            const data = await respuesta.json();

            if (data.ok) {
                mostrarAlerta(
                    accion === "cobrar"
                        ? `Venta ${data.numero_venta} registrada correctamente. Redirigiendo...`
                        : `Venta ${data.numero_venta} guardada como pendiente. Redirigiendo...`,
                    "success"
                );
                setTimeout(function () {
                    window.location.href = data.redirect_url;
                }, 600);
                return;
            }

            mostrarAlerta(data.error || "No se pudo procesar la venta.");
        } catch (error) {
            console.error("Error al procesar la venta en SIGEPAN:", error);
            mostrarAlerta("Ocurrió un error de comunicación con el servidor. Intente nuevamente.");
        } finally {
            botones.forEach(function (b) { b.disabled = false; });
        }
    }

    if (btnCobrar) {
        btnCobrar.addEventListener("click", function () {
            enviarVenta("cobrar");
        });
    }

    if (btnGuardarPendiente) {
        btnGuardarPendiente.addEventListener("click", function () {
            enviarVenta("pausar");
        });
    }

    // =====================================================
    // 11. CANCELAR VENTA (limpiar pantalla sin guardar nada)
    // =====================================================
    if (btnCancelar) {
        btnCancelar.addEventListener("click", function () {
            if (carrito.length === 0) return;

            if (confirm("¿Está seguro de que desea cancelar la venta actual? Se perderán los productos seleccionados.")) {
                carrito = [];
                renderizarCarrito();
                limpiarCliente();
                document.querySelectorAll(".metodo-pago-checkbox").forEach(function (cb) { cb.checked = false; });
                limpiarAlertas();
            }
        });
    }

    // =====================================================
    // 12. REANUDAR UNA VENTA PAUSADA
    // =====================================================
    // El carrito arranca directamente desde el JSON que sirvió
    // crear_venta() (detalles_activos_json) — sin pasar por ninguna
    // función puente ni por inputs ocultos indexados.
    const elProductosPendientes = document.getElementById("productos-pendientes-reanudados");
    const elClienteActivo = document.getElementById("cliente-activo-reanudado");

    const productosPendientesReanudados = elProductosPendientes
        ? JSON.parse(elProductosPendientes.textContent)
        : [];
    const clienteActivoReanudado = elClienteActivo
        ? JSON.parse(elClienteActivo.textContent)
        : null;

    if (productosPendientesReanudados && productosPendientesReanudados.length > 0) {
        carrito = productosPendientesReanudados.map(function (item) {
            return {
                producto_id: item.producto_id,
                nombre: item.nombre,
                precio: parseFloat(item.precio) || 0,
                cantidad: parseInt(item.cantidad, 10) || 1,
            };
        });
    }

    if (clienteActivoReanudado) {
        clienteIdInput.value = clienteActivoReanudado.id;
        clienteSeleccionadoSpan.textContent = clienteActivoReanudado.nombre;
    }

    // =====================================================
    // 13. RENDER INICIAL
    // =====================================================
    renderizarCarrito();
});
