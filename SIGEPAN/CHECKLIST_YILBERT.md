# Checklist de trabajo — Yilbert (SIGEPAN)

Entrega: viernes 8:00 p.m. · Última actualización: 2026-08-03

Leyenda: `[ ]` pendiente · `[~]` en progreso · `[x]` terminado

---

## FASE 0 — Bloqueante urgente (coordinar con César, no es tuyo pero te afecta)
- [ ] **RF-012 sigue bloqueante — es más grave de lo que parecía.** La línea 289 que calcula `venta.total` está en `guardar_venta_pendiente` (la función de "pausar venta"), NO en `crear_venta` (el checkout real del POS). Auditoría completa del módulo `ventas` encontró una cadena de 5+ bugs consecutivos que impiden guardar CUALQUIER venta hoy en día (confirmado: tabla `venta` vacía en la BD real):
  1. `crear_venta` nunca calcula `subtotal`/`impuesto`/`descuento`/`total` (solo `guardar_venta_pendiente` lo hace bien).
  2. Mismo bug que en `compras`: `Inventario.objects.filter(producto=..., sucursal=...)` en vez de `id_producto=`/`id_sucursal=` — en 3 lugares (crear_venta x2, anular_venta x1). `FieldError` inmediato al validar stock del primer producto.
  3. `DetallePago` (pagos divididos) mapea a una tabla `detalle_pago` que **no existe en la BD real** — la BD real solo soporta un método de pago por venta (`venta.id_metodo_pago`). Cualquier operación de pagos truena con `ProgrammingError`.
  4. `crear_venta.html` no tiene inputs para `metodo_pago`/`tipo_comprobante`/`impuesto`/`descuento` — el IVA que se ve en pantalla nunca se guarda en BD.
  5. Ninguna vista de `ventas` usa `SessionRequiredMixin`/`PermissionRequiredMixin`/`AuditMixin` — incluida `anular_venta`, que queda sin ningún control de acceso.
  - **Esto es de César, pero bloquea todo: no se puede tomar ni una captura de "venta completada" para el Entregable #5 hasta que se resuelva.** Avisarle hoy mismo con la lista de arriba, priorizando los puntos 1-3 (sin eso no hay ninguna venta posible).

## FASE 1 — Dashboard y exportaciones rápidas
- [x] **RF-020 Dashboard gerencial** — TERMINADO. Archivos: `backend/apps/dashboard/repositories.py`, `backend/apps/dashboard/services.py`, `backend/apps/dashboard/views.py`, `backend/apps/dashboard/templates/dashboard/*`.
  - [x] Repository con consultas reales (ventas del día/mes, cantidad, ticket promedio, top productos, ventas por sucursal)
  - [x] Service actualizado + `mostrar_kpis: True` (bug encontrado: la clave faltaba y las tarjetas nunca se mostraban)
  - [x] `SessionRequiredMixin` agregado a `DashboardView` (antes sin protección de sesión)
  - [x] Tarjetas de KPI + top productos + ventas por sucursal, verificado visualmente
  - [x] Restricción por rol agregada (mejora no documentada explícitamente en RF-020 pero exigida por la matriz de roles del Entregable #4: Cajero solo ve accesos rápidos; Administrador/Encargado ven todo) — verificado con usuario Cajero real
  - Pendiente futuro, no bloqueante: "diferencias de caja" y "mermas" en el dashboard (dependen de RF-017/RF-018, aún no implementados)
- [x] RF-021 Bitácora de ingresos — TERMINADO. Filtros + exportar PDF/Excel funcionando. Se centralizó el filtrado en `BitacoraService` (antes vivía duplicado en la vista).
- [x] RF-022 Bitácora de movimientos — TERMINADO. Se agregaron filtros (usuario/fecha, antes no tenía) + exportar PDF/Excel. Ambas exportaciones quedan registradas en la bitácora central (`registrar_log`, tipo `EXPORTAR`).
  - Archivos nuevos: `backend/apps/security/exports.py`
  - Archivos modificados: `security/services.py` (BitacoraService), `security/views.py` (4 vistas de exportación), `security/urls.py`, `security/templates/security/bitacora_ingresos/list.html`, `security/templates/security/bitacora_movimientos/list.html`
- [x] RF-008 Menú — TERMINADO (parte "Reportes"). Se agregó el grupo "Reportes" al diccionario `MENU` una vez que existían las URLs reales (se probó primero sin URLs y tumbó todo el sistema con `NoReverseMatch` — la lección: nunca apuntar el menú a una ruta que no existe todavía). "Dashboard" no necesitaba entrada de menú: ya es accesible vía "Inicio", que no depende de `MENU`.

## FASE 2 — Reportes operativos
- [x] RF-019 Reportes operativos — TERMINADO (alcance mínimo viable). App `backend/apps/reportes/` construida completa: repositories.py, services.py, exports.py (PDF/Excel genérico), views.py, urls.py, templates, módulo "Reportes" + permisos otorgados a Administrador/Supervisor, menú actualizado.
  - [x] Reporte de Ventas (filtros fecha/sucursal, exportar PDF/Excel) — verificado en navegador
  - [x] Reporte de Inventario (filtro sucursal + "bajo mínimo", exportar PDF/Excel) — verificado en navegador
  - Reporte por sucursal: cubierto por el Dashboard (RF-020), no se hizo vista dedicada aparte
  - No incluidos (fuera del alcance mínimo): reporte de mermas (depende de RF-017, no existe), reporte de actividad de usuarios
- [x] RF-025 Reporte tributario mensual — TERMINADO. Agrupa dinámicamente por método de pago (no se hardcodeó efectivo/SINPE/tarjeta). Verificado en navegador.
- [x] RF-027 Reporte de utilidad estimada — TERMINADO. Costos estimados = cantidad × precio_compra de cada detalle de venta del período. Verificado en navegador.

## FASE 3 — Cierre funcional
- [x] RF-024 Configuración tributaria — TERMINADO. Se creó tabla `datos_empresa` (SQL directo, siguiendo el flujo Database First del proyecto) + modelo Django `DatosEmpresa` (`managed = False`) + formulario + vista + menú ("Configuración → Datos de la Empresa"). Campo "Régimen tributario" implementado como lista desplegable (Régimen Tradicional / RTS / Otro, según Ministerio de Hacienda 2026) en vez de texto libre — mejora respecto al RF original. `ConfiguracionTributaria` (tasas de impuesto) se conserva aparte, sin tocar.
  - Nota: la carpeta `database/ddl/` estaba desactualizada (26 tablas vs. 42 reales); se usó el export real de la BD como referencia para este trabajo. Ver nota técnica arriba.
- [x] RF-031 Ayuda contextual — TERMINADO. Botón flotante "?" + modal, implementado con template tag de Django (`inclusion_tag`, sin JS/AJAX): `AyudaRepository.obtener_por_modulo_pantalla()`, `apps/ayuda/templatetags/ayuda_tags.py` (`boton_ayuda`), partial `ayuda/partials/boton_contextual.html`. Conectado a 4 pantallas: Dashboard, Productos, Ventas, Caja. Contenido real cargado vía la UI de administración de ayudas (RF-032, ya existía). Verificado en navegador en las 4 pantallas.
- [x] RF-034 Cambio de usuario — TERMINADO. Nueva vista `cambiar_usuario_view` + opción en el menú de usuario del navbar, distinta de "Cerrar sesión". Se registra en bitácora con descripción diferenciada (se reutilizó el tipo `LOGOUT` del catálogo real, ya que `CAMBIAR_USUARIO` no existe en el ENUM de `log_acciones` — evitamos tocar el ENUM bajo presión de tiempo).
- [x] Exportar reportes a Google Sheets (requisito del cliente, adicional a RF-023) — TERMINADO. Se construyó la funcionalidad completa: nueva columna `google_refresh_token` en `usuario` (SQL + modelo) para poder renovar el acceso sin pedirle al usuario que vincule su cuenta cada hora; `apps/reportes/google_sheets.py` (crea la hoja de cálculo en la cuenta de Google del usuario y escribe los datos); botón "Exportar a Google Sheets" agregado en los 4 reportes (ventas, inventario, tributario, utilidad), junto a los de PDF/Excel ya existentes. Verificado en navegador: abre una hoja nueva en Google Drive con los datos del reporte.
- [x] RF-023 — TERMINADO. Agregado el scope `https://www.googleapis.com/auth/spreadsheets` en `generar_url_google` y `procesar_callback_google` (`apps/security/services.py`), deben coincidir exactamente entre ambas funciones. Configurado también en Google Cloud Console (Google Auth Platform → Acceso a los datos → permiso agregado; cuenta de prueba ya en la lista de Usuarios de prueba, la app sigue en modo "Prueba" sin verificar). Verificado: vinculación de cuenta de Google reautorizada correctamente con el nuevo permiso.

## FASE 3.5 — Apoyo a César (según Excel de asignación, columna "Comentario" = YILBERT)
- [x] RF-016 Control de Inventario (responsable: César, apoyo: Yilbert) — TERMINADO. Bug corregido: `views.py` usaba `producto__nombre` en vez de `id_producto__nombre` (causaba error 500 en la lista); templates `lista_inventario.html` y `detalle_inventario.html` usaban `inventario.producto`/`inventario.sucursal` en vez de `inventario.id_producto`/`inventario.id_sucursal`. Verificado en navegador.
- [x] RF-028 Entrada de Inventario (responsable: César, apoyo: Yilbert) — TERMINADO. El backend (`MovimientoInventarioService`, repositorios) ya existía completo pero no lo usaba ninguna vista. Se construyó: `InventarioRepository.obtener_o_crear()`, `MovimientoInventarioForm`, `EntradaInventarioView` y `MovimientosInventarioListView` (con `SessionRequiredMixin`/`PermissionRequiredMixin`/`AuditMixin`), templates `entrada_inventario.html`/`lista_movimientos.html`, URLs, menú, y permisos CONSULTAR/CREAR sobre el módulo "Inventario" otorgados a Administrador y Supervisor vía shell. Verificado en navegador: entrada registrada, stock actualizado.
- [x] RF-029 Gestión de Clientes (responsable: César, apoyo: Yilbert) — verificado en código: CRUD completo (list/create/update/disable), repository+service reales, permisos y auditoría correctos. Confirmado COMPLETO, coincide con el Excel.
- [x] RF-030 Registro de Compras (responsable: César, apoyo: Yilbert) — TERMINADO Y PROBADO. Corregido `producto=`/`sucursal=` → `id_producto=`/`id_sucursal=` en `crear_compra`/`anular_compra`, conectado a `MovimientoInventarioService` (tipos `ENTRADA_COMPRA`/`DEVOLUCION_COMPRA`) + `InventarioRepository.obtener_o_crear()`. Bug adicional encontrado al probar: el modelo Django `Compra` no tenía el campo `sucursal` (`id_sucursal`), que en la BD real es `NOT NULL` sin default — causaba `IntegrityError` al guardar. Corregido: agregado el campo al modelo y auto-asignado desde `usuario_actual.id_sucursal` en la vista (igual que `usuario`). Verificado en navegador: compra registrada correctamente.
- [x] RF-010 Gestión de Categorías — TERMINADO. Eliminado el campo fantasma "Estado" del formulario de creación. Agregadas clases Bootstrap a los widgets (antes no tenían). Rediseñadas las 4 pantallas (lista, nueva, editar, cambiar_estado) con el estilo visual del resto del sistema (cards, badges, iconos). Verificado en navegador.
- [x] RF-011 Gestión de Productos — TERMINADO. Corregidos los 2 bugs: (1) subida de imagen funcional de punta a punta (`ImageField` real, `request.FILES`, `enctype`, guardado en `media/productos/`, servido en desarrollo vía `config/urls.py`); (2) `precio_venta` ahora se calcula server-side en `ProductoService.calcular_precio_venta()` (nuevo, `apps/productos/services.py`) más una vista previa en vivo por JS. Bug adicional encontrado y corregido: "Unidad de medida" era un campo sin opciones (formulario no se podía enviar) — se agregó `ChoiceField` con unidades reales de panadería. Pantalla "Gestión de Productos" migrada a Tabulator (buscador + tabla dinámica, igual que Clientes). Las 3 pantallas (lista, nuevo, editar) rediseñadas visualmente. Verificado en navegador.

## FASE 4 — Entregable #5 (viernes)
- [ ] 5.2 Lista de lenguajes/herramientas usadas (Python, Django, MySQL, VS Code, Git, ReportLab, OpenPyXL, Pandas, Google OAuth, Bootstrap5/crispy-forms) + reseña breve de cada una
- [ ] 5.3 Código fuente pegado por módulo/proceso
- [ ] 5.4.1 Pruebas de validación de datos (capturas)
- [ ] 5.4.2 Pruebas de control de acceso por rol (capturas)
- [ ] 5.4.3 Pruebas funcionales de inicio a fin (capturas)
- [ ] 5.4.4 Pruebas de carga de datos: grid del sistema vs. consulta SQL (capturas)
- [ ] 5.4.5 Pruebas de seguridad: login correcto/incorrecto, bitácoras, tabla usuario con password encriptado (capturas)
- [ ] 5.5 Bitácora de horas de programación y pruebas (fecha, horas, detalle)

---

## Notas técnicas encontradas en el camino
- La carpeta `database/ddl/` está desactualizada (26 tablas) frente a la base de datos real (42 tablas, ver export "BD Sigepan.sql" del 03-08-2026). Para cualquier cambio de esquema, usar el export real como referencia, no el DDL viejo.
- RF-017 (mermas) y RF-018 (ajustes): las tablas `merma` y `ajuste` **ya existen** en la base real con los campos correctos. Cuando se trabajen esos RF, solo hace falta crear el modelo Django (`managed = False`) + vistas — no hay que tocar SQL.
- `rol_permiso.fecha_creacion` en la base real sí permite NULL (`timestamp NULL DEFAULT CURRENT_TIMESTAMP`) — corrijo lo dicho en la auditoría: no truena con error, pero si Django no la asigna, guarda NULL en vez de la fecha real (silenciosamente pierde el dato). Igual vale la pena arreglarlo con `auto_now_add` cuando haya tiempo.
- El rol documentado como "Encargado" en el Entregable #4 está implementado en la base como "Supervisor" — mismo rol, nombre distinto. Ajustar el entregable o el código para que coincidan (cosmético, no urgente).
- Módulo "Reportes" creado en `configuracion.Modulo` + permiso CONSULTAR otorgado a Administrador y Supervisor vía shell de Django (no por la UI, que dio problemas). Pendiente: verificar por qué la UI de Asignación de Permisos no dejaba guardar, por si afecta a otros módulos.

## Notas — discrepancias entre tu Excel de seguimiento y el estado real del código
- RF-020: marcado "60-70% de avance" en el Excel; el código real tenía 0% de datos reales (solo placeholders). Ajustado en este checklist.
- RF-021, RF-022, RF-023, RF-024: marcados "COMPLETO" en el Excel; en el código están parciales (falta exportación en 021/022, falta scope de Sheets en 023, RF-024 implementa algo distinto a lo documentado).

## Historial de avance
- 2026-08-03: Checklist creado. Iniciando RF-020 (Dashboard).
- 2026-08-03: RF-020, RF-021, RF-022, RF-008 (parcial), RF-019, RF-025, RF-027, RF-024, RF-034 y RF-031 terminados. Solo queda RF-023 (opcional) en la parte de código.
- 2026-08-04: Se revisó el Excel de asignación de RF y se detectó apoyo pendiente a César en RF-016, RF-028, RF-029, RF-030. RF-016 y RF-028 terminados (bugs corregidos + pantalla de entrada de inventario construida desde cero). RF-029 verificado como completo. RF-030 con fix listo pero en pausa por coordinación con César.
- 2026-08-04: Auditoría completa del módulo de ventas: bug de `venta.total` era más grave de lo pensado (5+ bugs bloqueantes, ninguna venta se puede completar hoy). Reportado a César, quien se enfoca en resolverlo. RF-030 (compras) terminado y conectado con trazabilidad de inventario. RF-010 (categorías) y RF-011 (productos) revisados, corregidos (bugs de imagen, precio de venta, unidad de medida) y rediseñados visualmente (incluida migración de Productos a Tabulator). RF-023 terminado (scope de Google Sheets + refresh token) y se construyó la exportación a Sheets en los 4 reportes (requisito adicional del cliente).
- [x] Recuperación de contraseña por correo — revisado. No era un bug del sistema: SMTP, DNS (MX/SPF/DKIM/DMARC) y el código de envío estaban correctos; el correo llegaba pero caía en spam por el cuerpo de texto plano del correo (era solo un placeholder genérico, señal típica de spam). Corregido en `RecuperacionPasswordService.solicitar_recuperacion` (`security/services.py`): ahora el texto plano tiene contenido real con el enlace, más `reply_to`. Verificado: el correo llega (a veces a spam, normal en un dominio de envío nuevo/bajo volumen — no depende del código).
