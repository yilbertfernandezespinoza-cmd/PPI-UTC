# Checklist de desarrollo — SIGEPAN (34 RF)

> Última actualización: 2026-08-04 (noche) · Basado en: Auditoría base (02-08), CHECKLIST_YILBERT.md (03/04-08), verificación directa del código en `backend/apps/`, la corrección de RF-012/RF-016/RF-024/RF-030, los módulos nuevos RF-017/RF-018/RF-026, y el CRUD de RF-013 (métodos de pago) hechos en esta sesión.
> Marca `[x]` cuando el ítem esté verificado en código (no solo "hecho de memoria"). Actualiza el `% avance` de la cabecera al cerrar ítems.

## ⚠️ Antes de probar lo de hoy: acción requerida en tu máquina

Este entorno de trabajo no tiene MySQL ni una versión de Python compatible con Django 6.0.6 (solo hay
Python 3.10 disponible; Django 6.0 requiere 3.11+), así que todo lo de hoy se verificó con `py_compile`
(sintaxis, sobre **todo** `backend/apps` y `backend/config`, sin errores) y con una revisión manual línea por
línea contra los modelos y el DDL real — **no** se pudo correr contra tu base de datos real. `manage.py
check` (que sí corriste tú, dos veces) ya confirmó que **todo** el código de esta sesión está bien formado:
primero RF-012/016/024/030, y ahora también RF-017/018/026 (mermas, ajustes, gastos_operativos) y el CRUD de
RF-013 (métodos de pago) — `System check identified no issues (0 silenced)`. Solo falta:

1. ~~`python manage.py check`~~ ✅ confirmado en tu máquina el 04-08 (dos corridas, ambas limpias).
2. ~~`python manage.py seed_tipos_movimiento`~~ ✅ confirmado el 04-08 — sembró `MERMA` (los otros 8 ya
   existían).
3. ~~`python manage.py seed_permisos_modulos`~~ ✅ confirmado el 04-08 — creó los 3 módulos ("Mermas",
   "Ajustes", "Gastos Operativos"), sus 7 permisos y las 12 asignaciones a Administrador/Supervisor. (Se
   corrigió en el camino un bug del propio comando: `Modulo.orden_menu` es `NOT NULL` sin default y no se
   estaba enviando — ya calcula el siguiente número de orden automáticamente.)
4. ✅ Punta a punta parcial confirmado el 04-08 — encontraste 2 bugs reales durante la prueba (gracias por
   probar a fondo, esto es justo el propósito): `unidad_medida` bloqueando crear/editar productos (RF-011),
   y el POS de ventas fallando en silencio al cobrar + el carrito no reapareciendo al reanudar una venta
   pausada (RF-012). Los tres quedaron corregidos hoy mismo (ver detalle en las secciones RF-011/RF-012 más
   abajo). **Antes de seguir probando, en tu máquina:**
   - `python manage.py migrate productos` (aplica la migración 0002 de `unidad_medida`).
   - `python manage.py seed_metodos_pago` (crea Efectivo/Tarjeta/SINPE Móvil/Transferencia — sin esto el
     POS muestra una alerta de "no hay métodos de pago configurados" en vez de checkboxes).
   - `python manage.py check` de nuevo.
5. **Pendiente — repetir la prueba de punta a punta**: crear/editar un producto (el `<select>` de unidad de
   medida ya debe tener opciones) → abrir caja → venta completa (los checkboxes de pago ahora deben listar
   los métodos reales) → confirmar que se guarda y aparece en Ventas y en el dashboard → pausar una venta
   con productos en el carrito → "Ver Pendientes" → reanudarla → confirmar que el carrito reaparece →
   completarla → anularla → compra → anularla (RF-030) → registrar una merma → un ajuste de entrada y uno
   de salida → un gasto operativo con caja abierta y otro sin caja abierta. Revisar `inventario` y
   `movimiento_inventario` en cada caso → Configuración → Métodos de Pago (crear/editar, no debe permitir
   duplicados) → confirmar que los 3 módulos nuevos aparecen en el menú con el usuario Administrador.

**Leyenda:** `[x]` verificado en código · `[ ]` pendiente · 🔴 bug bloqueante · 🟡 riesgo/deuda técnica

## Protocolo de actualización (RF de César)

Cuando termines un RF (o un ítem puntual dentro de un RF), avísame en el chat de Cowork, por ejemplo:
"terminé RF-011" o "ya conecté el Service de inventario en compras (RF-016/RF-030)".

Antes de marcar la casilla, reviso el código real en `backend/apps/` (no me baso solo en tu palabra ni en el
Excel de seguimiento) — así evitamos el mismo problema que encontró la auditoría: RF marcados "COMPLETO" en
`RF ASIGNADOS.xlsx` que en el código estaban parciales o en 0%. Si algo no compila o falta una capa (permisos,
auditoría, validación), te lo señalo antes de cerrar el ítem, y solo marco `[x]` lo que quedó realmente
verificado — el resto se queda `[ ]` con lo que falta anotado.

---

## Resumen rápido de avance

| RF | Nombre | Resp. | % |
|---|---|---|---|
| RF-001 | Lenguaje Python | Yilbert | 100% |
| RF-002 | Motor MySQL | Yilbert | 100% |
| RF-003 | Framework Django | Yilbert | 100% |
| RF-004 | Control de accesos | Yilbert | 65% |
| RF-005 | Login | Yilbert | 90% |
| RF-006 | Gestión de usuarios | Yilbert | 100% |
| RF-007 | Roles y permisos | Yilbert | 100% |
| RF-008 | Menú principal | Yilbert | 85% |
| RF-009 | Gestión de sucursales | Yilbert | 100% |
| RF-010 | Gestión de categorías | César | 55% |
| RF-011 | Gestión de productos | César | 65% 🟡 (verificar en tu máquina) |
| RF-012 | Registro de ventas | César | 92% 🟡 (verificar en tu máquina) |
| RF-013 | Métodos de pago | César | 90% 🟡 (verificar en tu máquina) |
| RF-014 | Apertura de caja | César | 70% |
| RF-015 | Cierre de caja | César | 60% |
| RF-016 | Control de inventario | César/Yilbert | 75% 🟡 (verificar en tu máquina) |
| RF-017 | Registro de mermas | César | 80% 🟡 (verificar en tu máquina) |
| RF-018 | Anulación y ajustes | César | 75% 🟡 (verificar en tu máquina) |
| RF-019 | Reportes operativos | Yilbert | 80% |
| RF-020 | Dashboard gerencial | Yilbert | 85% |
| RF-021 | Bitácora de ingresos | Yilbert | 90% |
| RF-022 | Bitácora de movimientos | Yilbert | 90% |
| RF-023 | Vinculación Google | Yilbert | 55% |
| RF-024 | Configuración tributaria | Yilbert | 80% |
| RF-025 | Reporte tributario mensual | Yilbert | 85% |
| RF-026 | Gastos operativos | César | 75% 🟡 (verificar en tu máquina) |
| RF-027 | Reporte de utilidad estimada | Yilbert | 85% |
| RF-028 | Entrada de inventario | Yilbert (apoyo) | 85% |
| RF-029 | Gestión de clientes | César | 95% |
| RF-030 | Registro de compras | César | 80% 🟡 (verificar en tu máquina) |
| RF-031 | Ayuda contextual | Yilbert | 85% |
| RF-032 | Administración de ayudas | Yilbert | 70% |
| RF-033 | Acerca de | Yilbert | 95% |
| RF-034 | Cambio de usuario | César/Yilbert | 75% |

---

## 🔴 Bloqueantes — corregidos en código el 04-08 (tarde), pendientes de probar en tu máquina

- [x] **RF-012 (crear_venta)**: al revisar a fondo se encontró que el bug real era más grave de lo que se
  había registrado esta mañana: `venta.subtotal`, `venta.impuesto` y `venta.total` **nunca se calculaban**
  en `crear_venta()` (solo en `guardar_venta_pendiente()`, una función distinta) — la venta se rompía antes
  de llegar siquiera al bug de inventario. Corregido: el subtotal se calcula desde las líneas del carrito, el
  impuesto se calcula en el servidor a partir de `ConfiguracionTributaria` (nunca se confía en el 13%
  que el JS solo muestra en pantalla), y el total se arma con eso.
- [x] **RF-012 (crear_venta)**: además se encontró que `venta.metodo_pago` es `NOT NULL` en la base de datos
  real pero el formulario del POS no lo pide — se habría roto igual en el siguiente paso. Se deriva ahora
  automáticamente de las líneas de pago (un método → ese método; varios → "Mixto"; ninguno → "Pendiente",
  mismo patrón que ya usaba `guardar_venta_pendiente`).
- [x] **RF-012 (crear_venta y anular_venta)**: `Inventario.objects.filter(producto=..., sucursal=...)` con
  nombres de campo inexistentes, corregido en las tres ocurrencias del archivo. El descuento y la
  reintegración de stock ahora pasan por `MovimientoInventarioService` en vez de mutar `stock_actual` a mano.
- [x] **RF-030 (crear_compra y anular_compra)**: mismo error de nombres de campo corregido (2 ocurrencias).
  Además se corrigió el bug de "actualización de inventario que fallaba en silencio si no existía el
  registro" que ya había señalado la auditoría: `crear_compra` ahora usa `obtener_o_crear`, así que nunca más
  omite la entrada de stock sin avisar.
- [x] **RF-024**: eliminada la clase `DatosEmpresa` duplicada en `configuracion/models.py`.
- [ ] **Pendiente de ti**: correr `python manage.py check`, `python manage.py seed_tipos_movimiento`, y probar
  el flujo completo en tu máquina (ver el aviso al inicio del documento). Este entorno no tiene MySQL ni una
  versión de Python compatible con Django 6.0 para probarlo de punta a punta — la corrección se verificó por
  sintaxis (`py_compile`) y por revisión manual contra los modelos y el DDL real, no por ejecución real.

---

## RF-001 — Lenguaje de programación (Python)
**Completado**
- [x] Backend 100% Python bajo Django (manage.py, requirements.txt, todas las apps).

**Pendiente**
- [ ] Confirmar que la versión del entorno virtual coincide con la documentada (3.12+).

---

## RF-002 — Gestor de base de datos (MySQL)
**Completado**
- [x] `mysqlclient` en requirements, configuración vía `.env`, scripts DDL en `database/ddl/`.

**Pendiente**
- [ ] Consolidar en una sola fuente de verdad: hoy Entregable #4, DDL manual y migraciones Django no coinciden entre sí (ver nota en RF-002 de la auditoría base, tabla `producto`).

---

## RF-003 — Framework de desarrollo (Django)
**Completado**
- [x] `config/settings.py` + 14 apps Django completas bajo `backend/apps/`.

**Pendiente**
- [ ] Actualizar el Entregable #4: documenta Django 5.x, `requirements.txt` fija Django 6.0.6.

---

## RF-004 — Control de accesos
**Completado**
- [x] `security/permissions.py` (`PermissionRequiredMixin`) y `security/mixins.py` (`SessionRequiredMixin`) sobre `RolPermiso`.
- [x] Aplicado en: security, empleados, configuracion, ayuda, clientes.
- [x] Aplicado ahora también en: **inventario**, **dashboard** (nuevo desde el 02-08).

**Pendiente**
- [ ] Aplicar los mixins en **categorias, productos, proveedores, compras, caja, ventas** (6 de 14 apps siguen sin control de sesión/permisos — es la brecha de seguridad más grande del proyecto).

---

## RF-005 — Login
**Completado**
- [x] `login_view`, `RecuperacionPasswordService` (token firmado, expira 30 min), `make_password`/`check_password`.

**Pendiente**
- [ ] Bloqueo temporal tras N intentos fallidos consecutivos (rate limiting).
- [ ] Verificar en el template si existe botón "cancelar" (no verificable desde backend).

---

## RF-006 — Gestión de usuarios
**Completado**
- [x] `UsuarioListView`/`CreateView`/`UpdateView`/`DisableView` + `UsuarioForm` con validaciones de negocio.

**Pendiente**
- [ ] Ninguno detectado.

---

## RF-007 — Gestión de roles y permisos
**Completado**
- [x] `RolPermisoListView` (matriz de checkboxes) + `RolPermisoService.actualizar_permisos` con `@transaction.atomic`.

**Pendiente**
- [ ] 🟡 `RolPermiso.fecha_creacion` sin `auto_now_add` ni default — riesgo de `IntegrityError` en `get_or_create()`. Agregar `auto_now_add=True`.
- [ ] Investigar por qué la UI de Asignación de Permisos no dejaba guardar (nota dejada en checklist de Yilbert, 03-08) — podría afectar la asignación de permisos a nuevos módulos.

---

## RF-008 — Menú principal
**Completado**
- [x] `security/menu.py` + `MenuService.obtener_menu_usuario`, filtra por permisos `CONSULTAR` del rol.
- [x] Grupo "Reportes" agregado al diccionario `MENU`.

**Pendiente**
- [ ] "Salir" sigue hardcoded en `navbar.html` en vez de generarse dinámicamente.
- [ ] "Acerca de" sigue anidado dentro de "Seguridad" (ubicación cuestionable).

---

## RF-009 — Gestión de sucursales
**Completado**
- [x] `configuracion.Sucursal(BaseModel)` con CRUD, permisos y auditoría completos.

**Pendiente**
- [ ] Ninguno detectado.

---

## RF-010 — Gestión de categorías
**Completado**
- [x] CRUD funcional (listar, crear, editar, cambiar estado) en `categorias/views.py`.

**Pendiente**
- [ ] `Categoria` no hereda `BaseModel` (campos `estado`/`fecha_creacion`/`fecha_actualizacion` redefinidos manualmente).
- [ ] `repositories.py` y `services.py` vacíos (solo comentario de plantilla).
- [ ] Sin `SessionRequiredMixin`/`PermissionRequiredMixin` — cualquier usuario con la URL puede crear/editar sin autenticarse.
- [ ] Sin auditoría (no registra en `log_acciones`).
- [ ] Validación de duplicados vive en `forms.ValidationError` en vez de en un Service.

---

## RF-011 — Gestión de productos
**Completado**
- [x] CRUD en `productos/views.py` + endpoint `buscar_producto_pos` (JSON) usado por el POS.
- [x] **Bug reportado por César (04-08, sesión de pruebas): no se podía crear ni actualizar ningún
  producto.** Causa real: `unidad_medida` era un `CharField` sin `choices`, pero el formulario lo
  renderiza con `forms.Select` — un `<select>` completamente vacío, sin ninguna opción que elegir, por lo
  que el campo (requerido) nunca podía validar. Se agregaron `choices` explícitos (Unidad, Docena,
  Kilogramo, Gramo, Libra, Litro, Mililitro, Paquete, Caja, Bolsa) directamente en el modelo — la columna
  sigue siendo `varchar(30)`, mismo tamaño, mismo tipo, así que los productos ya guardados no se ven
  afectados. Migración `0002_alter_producto_unidad_medida` agregada (`AlterField`, sin tocar datos).

**Pendiente**
- [ ] **Verificar en tu máquina**: `manage.py migrate productos` (aplica la migración 0002) y luego crear/
  editar un producto para confirmar que el `<select>` de Unidad de medida ya tiene opciones y el formulario
  guarda.
- [ ] `Repository`/`Service` vacíos; `Producto` no hereda `BaseModel`.
- [ ] Sin permisos ni auditoría.
- [ ] Sin campo `stock_minimo` en el modelo (vive en `Inventario`).
- [ ] 🟡 `precio_venta` se calcula solo en JavaScript del navegador — un POST directo puede fijar cualquier precio sin validación de servidor. Mover el cálculo a un Service server-side.

---

## RF-012 — Registro de ventas
**Completado**
- [x] Modelo `Venta` + `DetalleVenta` + `DetallePago` (soporta pago mixto/múltiples métodos, supera lo documentado).
- [x] `crear_venta()`: subtotal calculado desde las líneas del carrito; impuesto calculado en el servidor vía
  `calcular_impuesto_ventas()` (tasas activas de `ConfiguracionTributaria`, nunca el valor que muestra el JS);
  `venta.total` correctamente calculado antes de usarse. Antes de hoy esto no se calculaba en ningún punto de
  `crear_venta()` y la venta se rompía siempre — el bug era más profundo de lo que registraba la mañana.
- [x] `venta.metodo_pago` (NOT NULL en la BD real, sin campo en el formulario) ahora se deriva de las líneas
  de `DetallePago` vía `determinar_metodo_pago_venta()`.
- [x] `venta.fecha_creacion`/`fecha_actualizacion` asignadas explícitamente (antes se enviaban como `NULL`
  porque el modelo no usa `auto_now_add`, a diferencia de `Compra`).
- [x] Validación de stock con `select_for_update` (ahora vía `InventarioRepository.obtener_para_actualizar`,
  con los nombres de campo correctos: `id_producto`/`id_sucursal`).
- [x] El descuento de stock al vender y la reintegración al anular pasan por `MovimientoInventarioService`
  (tipos `SALIDA_VENTA` / `DEVOLUCION_VENTA`) en vez de mutar `stock_actual` a mano — deja rastro en
  `movimiento_inventario`.
- [x] `anular_venta()` ahora identifica al usuario que anula (antes no identificaba a nadie) y usa los
  nombres de campo correctos de `Inventario`.
- [x] **Migración de arquitectura (04-08): el carrito del POS abandonó por completo los Django formsets y
  pasó a un flujo JSON/AJAX.** Historial que llevó a esta decisión — tres rondas de debugging sobre el
  mismo enfoque (formset armado a mano en JS con inputs ocultos `detalle-N-*`/`pago-N-*`):
  1. **Método de pago con código de texto en vez de PK real.** `DetallePago.metodo_pago` es una FK
     obligatoria a `MetodoPago`, pero los checkboxes del POS enviaban códigos fijos (`"EFECTIVO"`,
     `"TARJETA"`, ...) en vez de un `id_metodo_pago` real → `pago_formset.is_valid()` fallaba en todo
     cobro real, sin ningún `messages.error(...)` visible. Se corrigió generando los checkboxes desde el
     catálogo real de `MetodoPago` — pero el enfoque de formset seguía siendo frágil.
  2. **`window.agregarAlCarritoDirecto` no existía** al reanudar una venta pausada: el carrito nunca se
     repoblaba visualmente porque esa función puente nunca se había definido en `producto_pos.js`.
  3. **Bug final y definitivo:** `"id_detalle_venta: Este campo es obligatorio"` al guardar una venta
     pendiente. Django agrega un campo oculto para la PK de cada fila del formset; con la PK renombrada
     (no se llama `id`) y las filas armadas fuera del render estándar de Django, ese campo seguía
     exigiéndose incluso después de forzar `required=False` explícitamente sobre él vía un mixin
     (`_FormSetPkOpcionalMixin`) — el comportamiento no se podía confirmar sin ejecutar contra una base de
     datos real, y cada intento de "parchar" el formset generaba un bug distinto en el mismo lugar.

  **Decisión:** en vez de seguir depurando el mismo mecanismo, se eliminó por completo. El carrito ahora
  vive como un array de JavaScript (`carrito = []`, fuente de verdad única en el navegador,
  `venta_pos.js`) y se envía completo como un único JSON (`fetch()`, `Content-Type: application/json`) a
  una vista nueva, `apps.ventas.views.procesar_venta` (`POST /ventas/procesar/`,
  `name="ventas:procesar_venta"`), que reemplaza la lógica POST que antes tenían `crear_venta()` y
  `guardar_venta_pendiente()`. Ya no hay nombres de campo indexados, ni inputs ocultos de PK, ni
  `inlineformset_factory` — `DetalleVentaForm`, `DetallePagoForm`, `DetalleVentaFormSet`,
  `DetallePagoFormSet` y `_FormSetPkOpcionalMixin` se eliminaron de `apps/ventas/forms.py`
  (`pausar_venta()` también se eliminó de `views.py`/`urls.py`: se confirmó por grep que ningún template la
  referenciaba). `VentaForm` también se eliminó — ya no se usa en ningún lado.

  Contrato JSON de `procesar_venta` (ver docstring completo en `apps/ventas/views.py`):
  ```json
  {
    "accion": "cobrar" | "pausar",
    "cliente_id": 5 | null,
    "tipo_comprobante": "TICKET",
    "productos": [{"producto_id": 12, "cantidad": 2}],
    "pagos": [{"metodo_pago_id": 3, "monto": "150.00", "referencia": ""}]
  }
  ```
  Respuesta: `{"ok": true, "id_venta": ..., "numero_venta": "...", "redirect_url": "..."}` en éxito, o
  `{"ok": false, "error": "mensaje claro"}` con HTTP 400 en error — el frontend ahora sí puede mostrar el
  motivo real de cualquier fallo, en vez de que el POS "se reinicie" en silencio.

  Reglas que se preservaron sin cambios de la versión con formset (solo cambió de dónde leen los datos):
  `precio_unitario`/`subtotal` **nunca** se leen del JSON del navegador — se recalculan siempre en el
  servidor desde `Producto.precio_venta`; `calcular_impuesto_ventas()` sigue siendo la única fuente de
  verdad del impuesto; la validación/bloqueo de stock sigue pasando por
  `InventarioRepository.obtener_para_actualizar` + `MovimientoInventarioService.registrar_movimiento`
  (tipo `SALIDA_VENTA`); `determinar_metodo_pago_venta()` sigue derivando `venta.metodo_pago` de las
  líneas de pago; se sigue exigiendo caja abierta y se sigue creando un `MovimientoCaja` tipo `"VENTA"`.
  Decisión nueva: **pausar una venta no toca inventario** (igual que antes hacía
  `guardar_venta_pendiente()`) — el stock se valida y descuenta únicamente al cobrar de verdad, porque
  entre pausar y retomar puede cambiar por otra venta/ajuste/merma; reservarlo en la pausa daría una falsa
  sensación de reserva que el sistema no implementa.

  De regalo, se corrigió un bug de doble codificación JSON detectado durante la migración: la vista pasaba
  `detalles_activos_json` ya serializado con `json.dumps()` y el template le aplicaba encima el filtro
  `|json_script`, que serializa otra vez — el navegador recibía un *string* con JSON escapado adentro en
  vez de un arreglo, y `JSON.parse(...)` devolvía un string, no un array (`.map is not a function`, error
  no capturado). Ahora la vista pasa el objeto Python crudo (`detalles_activos`, lista de dicts) y el
  template lo serializa una sola vez con `|json_script`.
- [x] **Cuadrícula de categorías + productos (pedido explícito de César)**: `crear_venta.html` ahora
  muestra pestañas de categoría (`apps/categorias/models.py::Categoria`, activas) arriba de una cuadrícula
  de tiles grandes y tocables (nombre + precio, un tap agrega 1 unidad al carrito con feedback visual). El
  buscador de texto original se conserva junto a la cuadrícula para cuando el cajero prefiere escribir.
  Ambos consumen el mismo endpoint, `apps.productos.views.buscar_producto_pos`
  (`/productos/pos/buscar/`), extendido de forma retrocompatible con un parámetro opcional
  `categoria_id` (sin él, el comportamiento es idéntico al de siempre: mínimo 2 caracteres, top 10
  resultados por `?q=`; con `categoria_id`, ignora el mínimo de caracteres y devuelve hasta 60 productos de
  esa categoría).

**Pendiente**
- [ ] **Verificar en tu máquina (con `manage.py` real y MySQL) antes de dar por cerrado el módulo:**
  1. `python manage.py check` (no se pudo correr en el entorno de esta migración: Python 3.10 en el
     sandbox, Django 6.0.6 requiere 3.11+ para algunos imports internos — limitación conocida, no del
     código).
  2. Flujo de punta a punta en el POS: tocar una pestaña de categoría → confirmar que aparecen los tiles de
     producto correctos → tocar un tile → confirmar que aparece en el carrito con cantidad 1 → repetir el
     tap sobre el mismo tile y confirmar que suma cantidad en vez de duplicar la fila → usar el buscador de
     texto para agregar otro producto → cambiar una cantidad directamente en la tabla del carrito →
     eliminar una fila.
  3. Cobro: marcar uno o varios métodos de pago, tocar "Procesar Cobro", confirmar que redirige al detalle
     de la venta, que el total coincide, que el inventario bajó (`Inventario` + `movimiento_inventario`
     tipo `SALIDA_VENTA`) y que se creó el `MovimientoCaja` tipo `VENTA`.
  4. Pausa/reanudación: armar un carrito, tocar "Pausar / Guardar Venta", confirmar que aparece en "Ver
     Pendientes" con el total correcto, tocar "Retomar", confirmar que el carrito reaparece con los mismos
     productos/cantidades (este es el flujo que antes fallaba con "Este campo es obligatorio"), y confirmar
     que el inventario **no** bajó todavía. Cobrar esa venta retomada y confirmar que ahí sí baja el
     inventario una sola vez (no doble).
  5. Casos de error: intentar cobrar sin métodos de pago seleccionados, con stock insuficiente, y con el
     monto pagado menor al total — confirmar que en los tres casos aparece un mensaje de error legible en
     `#pos_alertas` (no un "reinicio" silencioso de la pantalla) y que la venta NO quedó guardada a medias.
  6. Anulación (`ventas:anular_venta`, sin cambios en esta migración): anular una venta ya cobrada y
     confirmar que el inventario se reintegra.
  7. **Atención especial**: el estimado de IVA que ve el cajero en pantalla (JS, 13% fijo) es solo un
     preview visual — si `ConfiguracionTributaria` tiene una tasa activa distinta de 13%, el monto de pago
     que el JS pre-llena al distribuir entre métodos de pago puede quedar por debajo del total real que
     calcula el servidor, y `procesar_venta` rechazará el cobro con "monto pagado menor al total". No es un
     bug nuevo de esta migración (el JS anterior también asumía 13% fijo), pero conviene probarlo si la
     tasa configurada no es exactamente 13%.
- [ ] `Repository`/`Service` propios de `ventas` (`apps/ventas/repositories.py`, `apps/ventas/services.py`)
  siguen vacíos; sin `PermissionRequiredMixin`/`AuditMixin` en las vistas (RF-004) — deuda técnica conocida,
  no se tocó en esta migración a propósito (fuera de foco).
- [ ] El consecutivo de `numero_venta` se calcula sin bloqueo — riesgo de colisión en concurrencia.
- [ ] Revisar si algún flujo sigue registrando `MovimientoCaja` con tipo `"ANULACION"` (no está en `TIPOS_MOVIMIENTO` de `caja/models.py`).

---

## RF-013 — Gestión de métodos de pago
**Completado**
- [x] `MetodoPago` corregido: `__str__` con `return` duplicado eliminado; ahora hereda `BaseModel`
  (timestamps automáticos, `estado` reutilizable) manteniendo `managed=False`/`db_table="metodo_pago"` —
  mismo bug de "fecha_creacion en NULL" que se corrigió hoy en `Venta`, y `nombre` ahora es `unique=True`.
- [x] CRUD completo agregado dentro de `apps/configuracion` (mismo app donde ya vive el modelo, junto a
  Sucursal/Configuración Tributaria — se reutiliza el módulo de permisos "Configuración" ya existente en
  vez de crear uno nuevo redundante):
  `MetodoPagoForm` (con `clean_nombre` que valida duplicados case-insensitive, excluyendo la instancia
  actual en edición), `MetodoPagoListView`/`MetodoPagoCreateView`/`MetodoPagoUpdateView`
  (`SessionRequiredMixin` + `PermissionRequiredMixin` + `AuditMixin`, permission_module="Configuración"),
  rutas `metodos-pago/`, `metodos-pago/nuevo/`, `metodos-pago/<id>/editar/`, templates
  `configuracion/metodos_pago/{list,form}.html` (mismo patrón Tabulator + `puede_crear`/`puede_modificar`
  que `tributaria/list.html`), y entrada de menú "Métodos de Pago" bajo el grupo "Configuración".
- [x] Verificado: no hay otro código en el proyecto que cree `MetodoPago` pasando `fecha_creacion`
  explícita (el único `get_or_create` existente, en `ventas/utils.py::determinar_metodo_pago_venta` para
  "Mixto"/"Pendiente", no la pasa) — el cambio a `BaseModel` es seguro y de hecho corrige de forma
  colateral el mismo bug de `fecha_creacion` en NULL para esas filas creadas automáticamente.

**Pendiente**
- [ ] **Verificar en tu máquina**: `manage.py check`, luego navegar a Configuración → Métodos de Pago,
  crear/editar un método y confirmar que la tabla, el formulario y los mensajes se ven correctamente.
- [ ] No se agregó vista de deshabilitar/activar independiente — el toggle de `estado` se hace desde el
  mismo formulario de edición (igual que Sucursal/Configuración Tributaria); si se necesita una acción
  rápida de un clic desde la lista, se puede agregar después sin romper nada de lo ya construido.
- [ ] `managed=False` sigue sin documentar formalmente cómo se puebla/versiona la tabla `metodo_pago` (no
  bloquea el CRUD, pero si faltan filas base tipo "Efectivo"/"Tarjeta" hay que crearlas manualmente o via
  un futuro comando `seed_metodos_pago`).

---

## RF-014 — Apertura de caja
**Completado**
- [x] `caja.AperturaCaja` + vista `abrir_caja`, valida que no exista una apertura activa previa.

**Pendiente**
- [ ] Campo `turno` no existe ni en el modelo ni en el DDL (sí es parte del texto del RF).
- [ ] `Repository`/`Service` vacíos; validación con `if/else` en vez de `ValidationError`.
- [ ] Permisos verificados con función propia `es_administrador()` en vez de `PermissionRequiredMixin` (duplica lógica ya centralizada en `security`).

---

## RF-015 — Cierre de caja
**Completado**
- [x] `CierreCaja` + `ArqueoCaja` (`saldo_sistema`, `saldo_contado`, `diferencia`).

**Pendiente**
- [ ] Campo `turno` ausente (mismo caso que RF-014).
- [ ] Cierre y arqueo repartidos en dos modelos distintos sin documentar la relación.
- [ ] Sin auditoría central (solo `HistorialCaja` propio, desconectado de `log_acciones`).
- [ ] Sin `ValidationError`.

---

## RF-016 — Control de inventario
**Completado**
- [x] `Inventario` + `MovimientoInventario` + `TipoMovimientoInventario` (heredan `BaseModel`, bien diseñados).
- [x] `InventarioRepository` y `MovimientoInventarioService.registrar_movimiento` con `ValidationError` si el stock quedaría negativo.
- [x] Bug corregido: `producto__nombre` → `id_producto__nombre` en vistas y templates de lista/detalle.
- [x] `SessionRequiredMixin`/`PermissionRequiredMixin` aplicados en las vistas de inventario.
- [x] `InventarioRepository` ampliado con `obtener_por_producto_sucursal()` y `obtener_para_actualizar()`
  (con `select_for_update`) — punto único de acceso a Inventario, ya no cada app repite su propia consulta
  con nombres de campo distintos.
- [x] **`ventas` y `compras` ahora usan `MovimientoInventarioService`** en vez de mutar `stock_actual` a
  mano: venta (`SALIDA_VENTA`), anulación de venta (`DEVOLUCION_VENTA`), compra (`ENTRADA_COMPRA`), anulación
  de compra (`DEVOLUCION_COMPRA`) — la recomendación de mayor beneficio de la auditoría, aplicada.
- [x] Comando `seed_tipos_movimiento` para sembrar el catálogo de 8 tipos de movimiento que necesita el
  Service (idempotente, no toca datos existentes).

**Pendiente**
- [ ] **Ejecutar `python manage.py seed_tipos_movimiento` en tu base de datos real** antes de probar ventas o
  compras — si el catálogo no tiene esas filas, `crear_venta`/`crear_compra` muestran un mensaje de error
  claro (no un `FieldError` críptico) pero no van a completar la operación.
- [ ] RF-017/RF-018 (mermas, ajustes) todavía no existen como modelo — cuando se implementen, deben conectarse
  al mismo Service (tipos `AJUSTE_POSITIVO`/`AJUSTE_NEGATIVO`, ya contemplados).

---

## RF-017 — Registro de mermas
**Completado**
- [x] Tabla `merma` ya existe en la BD real con los campos correctos (producto, usuario, cantidad, motivo, fecha, observaciones).
- [x] App `mermas/` completa: `models.py` (`Merma`, `managed=False` — la tabla real no tiene `estado` ni
  `fecha_actualizacion`, así que NO hereda `BaseModel` como el resto; es un registro histórico, no editable),
  `repositories.py`, `services.py`, `forms.py`, `views.py`, `urls.py`, templates (`list.html`, `form.html`,
  `detalle.html`).
- [x] `MermaService.registrar()` descuenta stock real vía `MovimientoInventarioService` con un tipo de
  movimiento nuevo, `MERMA` (separado de `AJUSTE_NEGATIVO` a propósito: son eventos de negocio distintos).
  Nunca guarda la merma sin afectar el inventario.
- [x] El formulario solo ofrece productos con existencias en la sucursal del usuario.
- [x] `SessionRequiredMixin`/`PermissionRequiredMixin`/`AuditMixin` en las tres vistas (listar, ver, registrar).
- [x] Filtros por producto y rango de fechas en el listado.
- [x] Conectado al menú (grupo Operaciones) y a `config/urls.py`/`INSTALLED_APPS`.
- [x] `tests.py` con pruebas de validación del formulario (cantidad > 0, motivo obligatorio).

**Pendiente**
- [ ] **Verificar en tu máquina**: `manage.py check`, `seed_tipos_movimiento` (nuevo tipo `MERMA`),
  `seed_permisos_modulos` (nuevo, crea el módulo "Mermas" y sus permisos — sin esto nadie puede ver el menú
  ni la pantalla), y probar registrar una merma real.
- [ ] No hay reporte de mermas dedicado todavía (lo anotaba RF-019 como pendiente); ahora que el modelo
  existe, se puede agregar a `apps/reportes` o al Dashboard (RF-020 lo dejó pendiente explícitamente).
- [ ] Sin edición ni anulación de una merma ya registrada — decisión de diseño (es un historial), pero
  confírmalo: si el negocio sí necesita corregir una merma mal cargada, hace falta un flujo de reversa (un
  ajuste de entrada que la compense, dejando ambos registros, no editar/borrar la merma original).

---

## RF-018 — Registro de anulación y ajustes
**Completado**
- [x] `anular_venta` (ventas) devuelve stock al inventario vía `MovimientoInventarioService` (tipo
  `DEVOLUCION_VENTA`) y registra un movimiento de caja.
- [x] Tabla `ajuste` ya existe en la BD real (tipo ENTRADA/SALIDA y motivo).
- [x] App `ajustes/` completa: `models.py` (`Ajuste`, `managed=False`, mismo criterio que Merma — sin
  `estado`/`fecha_actualizacion` en la tabla real, registro histórico no editable), con `tipo` como
  `TextChoices` (ENTRADA/SALIDA), `repositories.py`, `services.py`, `forms.py`, `views.py`, `urls.py`,
  templates.
- [x] `AjusteService.registrar()`: ENTRADA usa `AJUSTE_POSITIVO` (y crea el inventario si no existía —
  corrige una omisión); SALIDA usa `AJUSTE_NEGATIVO` y exige que el inventario ya exista, respetando la
  regla de no dejar stock negativo (la misma validación de `MovimientoInventarioService`).
- [x] Permisos, auditoría, filtros por producto/tipo/fecha en el listado.
- [x] Conectado al menú, urls e `INSTALLED_APPS`.
- [x] `tests.py` con pruebas de validación del formulario.

**Pendiente**
- [ ] **Verificar en tu máquina** — mismo aviso que RF-017.
- [ ] `"ANULACION"` sigue sin estar declarado en `TIPOS_MOVIMIENTO` de `caja/models.py` — ya no se encontró
  ningún flujo que lo use (se revisó `anular_venta`, usa tipo `"VENTA"` de caja, no `"ANULACION"`), así que
  probablemente ya no aplica; de todas formas no se tocó el catálogo de caja en esta sesión.
- [ ] Sin número de documento propio para el ajuste (el RF original lo menciona) — hoy se identifica solo
  por `id_ajuste`; evaluar si hace falta un folio con formato propio.

---

## RF-019 — Reportes operativos
**Completado**
- [x] App `reportes/` construida completa: `repositories.py`, `services.py`, `exports.py` (PDF/Excel), `views.py`, `urls.py`, templates.
- [x] Reporte de Ventas (filtros fecha/sucursal, exportar PDF/Excel) — verificado en navegador.
- [x] Reporte de Inventario (filtro sucursal + "bajo mínimo", exportar PDF/Excel) — verificado en navegador.
- [x] Módulo "Reportes" + permisos otorgados a Administrador/Supervisor, menú actualizado.

**Pendiente**
- [ ] Reporte por sucursal dedicado (hoy cubierto indirectamente por el Dashboard).
- [ ] Reporte de mermas (depende de RF-017, aún no existe).
- [ ] Reporte de actividad de usuarios.
- [ ] Permisos otorgados vía shell de Django, no por la UI (la UI de asignación de permisos dio problemas — ver nota RF-007).

---

## RF-020 — Dashboard gerencial
**Completado**
- [x] `DashboardRepository` con consultas reales (`Sum`/`Avg` sobre `Venta`/`DetalleVenta`): ventas del día/mes, cantidad, ticket promedio, top productos, ventas por sucursal.
- [x] `mostrar_kpis: True` corregido (antes faltaba la clave y las tarjetas nunca se mostraban).
- [x] `SessionRequiredMixin` agregado a `DashboardView`.
- [x] Restricción por rol (Cajero ve solo accesos rápidos; Administrador/Supervisor ven todo) — verificado con usuario Cajero real.

**Pendiente**
- [ ] "Diferencias de caja" en el dashboard (depende de RF-018, ajustes).
- [ ] "Mermas" en el dashboard (depende de RF-017).

---

## RF-021 — Bitácora de ingresos
**Completado**
- [x] `BitacoraIngresosListView` con filtros por usuario y rango de fechas.
- [x] Exportación a PDF y Excel funcionando vía `security/exports.py`.
- [x] Exportaciones registradas en la bitácora central (`registrar_log`, tipo `EXPORTAR`).

**Pendiente**
- [ ] Exportación a Google Sheets (depende del scope de RF-023, no habilitado).

---

## RF-022 — Bitácora de movimientos
**Completado**
- [x] `BitacoraMovimientosListView` con filtros (usuario/fecha) — antes no tenía.
- [x] Exportación PDF/Excel funcionando (mismo módulo que RF-021).

**Pendiente**
- [ ] Exportación a Google Sheets (igual que RF-021).

---

## RF-023 — Vinculación de cuenta Google
**Completado**
- [x] `generar_url_google`/`procesar_callback_google`/`google_vincular`/`google_desvincular` con OAuth 2.0 real (`google-auth-oauthlib`).

**Pendiente**
- [ ] El scope solicitado solo cubre `openid`/`email`/`profile` — falta el scope de `spreadsheets` (Google Sheets) para habilitar exportación a Sheets en RF-021/022.
- [ ] Los bloques `except Exception` de los flujos de Google no registran tipo `ERROR` en la bitácora pese a existir ese valor en el catálogo.

---

## RF-024 — Configuración tributaria
**Completado**
- [x] Modelo `DatosEmpresa` (tabla real `datos_empresa`, creada por SQL directo — Database First) con formulario, vista y menú ("Configuración → Datos de la Empresa").
- [x] "Régimen tributario" como lista desplegable (Tradicional / RTS / Otro) en vez de texto libre.
- [x] `ConfiguracionTributaria` (tasas de impuesto) conservado sin tocar.
- [x] Clase `DatosEmpresa` duplicada eliminada de `configuracion/models.py` — queda una sola definición.
- [x] `ConfiguracionTributaria` ahora tiene un consumidor real además del CRUD propio: `calcular_impuesto_ventas()` (RF-012) la usa para calcular el impuesto de cada venta.

**Pendiente**
- [ ] Regenerar/confirmar migraciones si aplica.

---

## RF-025 — Reporte tributario mensual
**Completado**
- [x] Vista en `apps/reportes` con agrupación dinámica por método de pago (no hardcodeado efectivo/SINPE/tarjeta) — verificado en navegador.

**Pendiente**
- [ ] Ninguno crítico detectado; validar con capturas para el Entregable #5.

---

## RF-026 — Registro de gastos operativos
**Completado**
- [x] Tabla `gasto_operativo` ya existe en la BD real (sucursal, categoría, descripción, monto, comprobante).
- [x] App `gastos_operativos/` completa: `models.py` (`GastoOperativo(BaseModel)` — esta tabla sí tiene
  `estado`/`fecha_actualizacion`, a diferencia de merma/ajuste, así que sí hereda `BaseModel` y sí permite
  deshabilitar un gasto cargado por error sin borrarlo), `repositories.py`, `services.py`, `forms.py`
  (`forms.Form`, no `ModelForm` — sucursal/usuario/caja se resuelven en el Service, no se le piden a quien
  registra), `views.py`, `urls.py`, templates.
- [x] **Conectado al saldo real de caja**: si el usuario tiene una `AperturaCaja` activa, el gasto se vincula
  a esa caja Y se crea un `MovimientoCaja` tipo `"GASTO"` — ese tipo ya existía en el catálogo de caja y
  `calcular_saldo_sistema()` (`caja/utils.py`) ya lo resta del saldo; no era necesario tocar nada de caja
  para que esta integración funcionara. Si no hay caja abierta (gasto administrativo, ej. alquiler), se
  guarda igual con `caja` en blanco — el campo ya era nullable en la BD real para este caso.
- [x] CRUD con deshabilitar/habilitar (permiso `ELIMINAR`, mismo patrón que Clientes/Categorías), filtros por
  sucursal/categoría/fecha, permisos y auditoría.
- [x] `tests.py` con pruebas de validación del formulario.

**Pendiente**
- [ ] **Verificar en tu máquina** — mismo aviso que RF-017/RF-018, con énfasis en probar ambos casos (con y
  sin caja abierta) y confirmar que el saldo de caja realmente refleja el gasto.
- [ ] Sin campo de comprobante/factura adjunta (el RF menciona "comprobante" como dato) — hoy solo hay
  `observaciones` de texto libre; si se necesita adjuntar una imagen/PDF del comprobante, hace falta agregar
  un campo de archivo (columna nueva, no rompe lo existente).
- [ ] La categoría es una lista sugerida en el formulario pero el campo en BD es texto libre — no hay
  catálogo `CategoriaGasto` dedicado; suficiente para el alcance del RF, pero si se necesita reportar por
  categoría de forma más estricta convendría un catálogo real.

---

## RF-027 — Reporte de utilidad estimada
**Completado**
- [x] Vista en `apps/reportes`: costo estimado = cantidad × `precio_compra` por línea de venta del período — verificado en navegador.

**Pendiente**
- [ ] Ninguno crítico detectado; validar con capturas para el Entregable #5.

---

## RF-028 — Entrada de inventario
**Completado**
- [x] `InventarioRepository.obtener_o_crear()`.
- [x] `MovimientoInventarioForm`, `EntradaInventarioView`, `MovimientosInventarioListView`.
- [x] `SessionRequiredMixin`/`PermissionRequiredMixin`/`AuditMixin` aplicados.
- [x] Templates, URLs y menú; permisos CONSULTAR/CREAR otorgados a Administrador y Supervisor.
- [x] Verificado en navegador: entrada registrada, stock actualizado.

**Pendiente**
- [ ] Ninguno crítico detectado.

---

## RF-029 — Gestión de clientes
**Completado**
- [x] `Cliente(BaseModel)`, `ClienteRepository`, `ClienteService` con `ValidationError`.
- [x] `validators.py` por tipo de identificación (cédula física, jurídica, DIMEX, pasaporte).
- [x] Permisos y auditoría completos — la app mejor implementada del proyecto.

**Pendiente**
- [ ] Migración `0001_initial` desincronizada del modelo actual (faltan `tipo_cliente`/`tipo_identificacion`). Regenerar con `makemigrations`.

---

## RF-030 — Registro de compras
**Completado**
- [x] `Compra` + `DetalleCompra` (`managed=False`, coherente con el DDL).
- [x] Vista `crear_compra` dentro de `@transaction.atomic`.
- [x] `Inventario.objects.filter(producto=..., sucursal=...)` corregido a `id_producto=`/`id_sucursal=` en
  `crear_compra` y `anular_compra`, vía `InventarioRepository`.
- [x] Ya **no** falla en silencio si no existe el registro de inventario: `crear_compra` usa
  `obtener_o_crear()`.
- [x] Ahora crea `MovimientoInventario` (tipos `ENTRADA_COMPRA` / `DEVOLUCION_COMPRA`) — se recupera la
  trazabilidad que la auditoría señaló como perdida.
- [x] `anular_compra` avisa explícitamente (`messages.warning`) si no encuentra el inventario de una línea,
  en vez de omitir el ajuste sin decir nada.

**Pendiente**
- [ ] **Verificar en tu máquina** — mismo aviso que RF-012/RF-016: no se pudo probar contra Django/MySQL
  reales en este entorno.
- [ ] `Repository`/`Service` propios de `compras` vacíos; sin `PermissionRequiredMixin`/`AuditMixin` en las
  vistas (RF-004).
- [ ] `HistorialPrecio` (documentada en Entregable #4) no implementada — decidir si se implementa o se retira del diseño.

---

## RF-031 — Módulo de ayuda contextual
**Completado**
- [x] Botón flotante "?" + modal vía `inclusion_tag` de Django (sin JS/AJAX).
- [x] `AyudaRepository.obtener_por_modulo_pantalla()`, `templatetags/ayuda_tags.py` (`boton_ayuda`), partial `ayuda/partials/boton_contextual.html`.
- [x] Conectado en 4 pantallas: **Dashboard, Productos, Ventas, Caja** — verificado en navegador.

**Pendiente**
- [ ] Conectar a las pantallas restantes (categorias, proveedores, compras, inventario, configuración, etc.) según se necesite.
- [ ] Manejo de manual en PDF (mencionado en el RF original, no implementado).

---

## RF-032 — Administración de ayudas
**Completado**
- [x] CRUD completo: `AyudaService` valida duplicados de (módulo, pantalla).
- [x] `AuditMixin` distingue "activar" de "desactivar" — junto con `clientes`, el mejor ejemplo de separación por capas del proyecto.

**Pendiente**
- [ ] Campo "código" explícito no existe.
- [ ] Campo "imagen" (`ImageField`) no existe — "icono" es solo una clase CSS, no una imagen.
- [ ] Migración inicial declara el módulo como `IntegerField` en vez de `ForeignKey` — regenerar migración.

---

## RF-033 — Acerca de
**Completado**
- [x] `core/views.py` + `core/system_info.py` con toda la información requerida (sistema, versión, empresa, desarrolladores, tecnologías, contacto).

**Pendiente**
- [ ] Información 100% codificada en diccionario Python en vez de base de datos (aceptable para este RF, ya que es información estática — no es bloqueante).

---

## RF-034 — Cambio de usuario
**Completado**
- [x] `cambiar_usuario_view()` implementada + opción en el menú de usuario del navbar, distinta de "Cerrar sesión".
- [x] Se registra en bitácora (reutiliza el tipo `LOGOUT` del catálogo real).

**Pendiente**
- [ ] No hay un tipo de evento propio (`CAMBIAR_USUARIO`) en el ENUM de `log_acciones` — hoy se registra como `LOGOUT`, sin diferenciar. Decidir si vale la pena tocar el ENUM o dejarlo documentado como decisión consciente.

---

## Deuda técnica transversal (no es un RF, pero bloquea "cerrar" varios)

- [ ] Migrar `Producto`, `Categoria`, `Proveedor`, `MetodoPago` a `BaseModel`.
- [ ] Reemplazar `ValueError` por `ValidationError` en los Service existentes (security, ayuda).
- [ ] Retirar `print()` de depuración en `security/views.py`.
- [ ] Decidir si `django-allauth` y `security/decorators.py::login_required` se usan o se retiran (hoy están sin uso).
- [ ] `proveedores` e `inventario` no declaran `managed=False` y no tienen `migrations/` — documentar o generar migraciones antes de un entorno nuevo.
- [ ] Actualizar Entregable #4 (estructura de BD y diccionario de datos) con el esquema real de 26 tablas.
- [x] `Venta.fecha_creacion`/`fecha_actualizacion` sin asignar en `crear_venta()` (mismo patrón de riesgo que
  el ya conocido en `RolPermiso.fecha_creacion`) — corregido el 04-08 al mismo tiempo que RF-012.
