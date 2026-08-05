// =====================================================
// SIGEPAN - Módulo: Ventas
// Archivo: producto_pos.js (DEPRECADO — 04-08-2026)
// =====================================================
//
// Este archivo ya NO se carga desde crear_venta.html. Toda su lógica
// (búsqueda de productos, control del carrito, reindexación de formset)
// se fusionó y reescribió en venta_pos.js como parte de la migración del
// POS de Django inlineformset_factory a un flujo JSON/AJAX.
//
// Motivo de la migración: el enfoque anterior armaba el carrito con
// inputs ocultos indexados ("detalle-0-producto", "detalle-0-cantidad",
// etc.) para calzar con DetalleVentaFormSet/DetallePagoFormSet
// (apps/ventas/forms.py, ya eliminados). Ese enfoque resultó frágil:
// bug de método de pago con texto en vez de PK real, bug de
// "agregarAlCarritoDirecto" al reanudar una venta pausada y, finalmente,
// un bug persistente de "id_detalle_venta: Este campo es obligatorio"
// que sobrevivió incluso forzando required=False sobre el campo de la
// PK del formset.
//
// Se conserva este archivo vacío (en vez de borrarlo) porque el entorno
// de desarrollo usado para esta migración no tuvo permisos para eliminar
// el archivo del disco. No define nada global ni se referencia desde
// ningún template: es seguro borrarlo manualmente en cualquier momento.
