# Spec: Profile Management
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-008 via prd-hogar-sad_discovery.md)
> Feature ID: F-008
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora del perfil CUIDEO (app Hogar) | Ver y editar perfil personal y profesional, gestionar foto de perfil, subir y consultar documentos personales, consultar documentos laborales, firmar documentos, ver porcentaje de completitud del perfil |
| Trabajadora SAD | Trabajadora del perfil Felizvita (app SAD) | Ver y editar perfil personal y profesional, gestionar foto de perfil, subir y consultar documentos personales, consultar documentos laborales, firmar documentos, ver estado del contrato |

---

## Historias de Usuario

### HU-001: Ver y editar información del perfil
Como trabajadora
quiero ver mi información personal y profesional organizada en secciones
para que pueda mantener mis datos actualizados y verificar que son correctos

### HU-002: Actualizar dirección de domicilio
Como trabajadora
quiero editar mi dirección de domicilio desde la app
para que el sistema pueda asignarme servicios en mi zona actualizada

### HU-003: Gestionar foto de perfil
Como trabajadora
quiero subir y actualizar mi foto de perfil desde la galería o la cámara
para que mi imagen sea reconocible por el equipo de coordinación

### HU-004: Proponer cambio en datos de identidad
Como trabajadora
quiero proponer la actualización de mi DNI/NIE con un documento justificativo
para que el backoffice pueda validar el cambio de forma segura

### HU-005: Consultar y subir documentación personal
Como trabajadora
quiero subir documentos personales (DNI/NIE, certificados) y consultar los que ya tengo registrados
para que mi expediente esté completo y actualizado

### HU-006: Consultar y firmar documentación laboral
Como trabajadora
quiero consultar mis documentos laborales (nóminas, contratos) y firmar los que requieran mi firma
para que pueda acceder a mi información laboral y formalizar los documentos pendientes sin desplazamientos

### HU-007: Capturar y reutilizar firma digital
Como trabajadora
quiero dibujar mi firma en pantalla y guardarla para usarla en futuras ocasiones
para que no tenga que volver a dibujarla cada vez que necesite firmar un documento

### HU-008: Completar perfil para aplicar a ofertas (solo Hogar)
Como trabajadora Hogar
quiero recibir una advertencia clara cuando mi perfil esté incompleto al intentar aplicar a una oferta
para que sepa exactamente qué campos debo completar antes de poder enviar mi solicitud

### HU-009: Ver estado del contrato (solo SAD)
Como trabajadora SAD
quiero consultar la información de mi contrato actual y descargar el PDF
para que tenga acceso a las condiciones de mi relación laboral en cualquier momento

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001]. Responde en el spec respondiendo el gap, luego ejecuta `/wf-spec-delta resolve` para completar.

---

## Recorridos de Usuario

### Journey 1: Ver y editar perfil
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar y actualizar su información de perfil

1. La trabajadora accede a la sección "Mi Perfil" desde la navegación principal.
2. El sistema muestra el perfil organizado en secciones: Personal, Profesional, Educación, Idiomas y, solo para SAD, Contrato.
3. La trabajadora identifica una sección con datos que desea editar y pulsa el botón de edición de esa sección.
4. El sistema activa los campos editables de la sección seleccionada (la dirección de domicilio es editable; los datos core como nombre, apellidos y DNI/NIE son de solo lectura en esta vista).
5. La trabajadora modifica los campos deseados y confirma los cambios.
6. El sistema valida los datos, guarda los cambios y muestra confirmación.

Estado de éxito: Los datos modificados se reflejan inmediatamente en el perfil. Los datos core no editables permanecen en modo lectura.
Flujos alternativos:
- Si la validación falla (formato de teléfono, email o DNI/NIE incorrecto) → el sistema muestra el mensaje de error en el campo correspondiente y no guarda los cambios.

---

### Journey 2: Subir y actualizar foto de perfil
Actor: Trabajadora (Hogar o SAD) | Objetivo: Cambiar su imagen de perfil

1. La trabajadora accede a su perfil y pulsa sobre la foto de perfil actual (o el placeholder si no tiene foto).
2. El sistema ofrece las opciones: elegir de galería o hacer una nueva foto con la cámara.
3. La trabajadora selecciona la imagen deseada.
4. El sistema muestra la herramienta de recorte con formato cuadrado; la trabajadora ajusta el encuadre y confirma.
5. El sistema optimiza el tamaño de la imagen y la sube al servidor mostrando el progreso de la operación.
6. La foto actualizada aparece en el perfil y en toda la aplicación.

Estado de éxito: La nueva foto es visible en el perfil y en todos los puntos de la app donde aparezca la imagen de la trabajadora.
Flujos alternativos:
- Si la imagen supera el límite de tamaño permitido → el sistema informa a la trabajadora y no inicia la subida.
- Si el formato no es compatible → el sistema informa a la trabajadora de los formatos admitidos.

---

### Journey 3: Consultar y descargar documentación laboral
Actor: Trabajadora (Hogar o SAD) | Objetivo: Acceder a sus nóminas y documentos laborales

1. La trabajadora accede a la sección de Documentos desde el perfil o desde el acceso rápido de la home.
2. El sistema muestra los documentos organizados en dos categorías: Documentación personal y Documentación laboral.
3. La trabajadora selecciona un documento laboral (ej. nómina).
4. El sistema abre el visor de documentos mostrando el contenido del archivo.
5. La trabajadora descarga el documento a su dispositivo si lo necesita.

Estado de éxito: La trabajadora puede visualizar y descargar sus documentos laborales. No puede subir ni eliminar documentos laborales desde la app.
Flujos alternativos: Ninguno relevante para este journey.

---

### Journey 4: Firmar un documento laboral pendiente
Actor: Trabajadora (Hogar o SAD) | Objetivo: Formalizar un documento que requiere su firma

1. La trabajadora recibe un aviso de documento pendiente de firma (desde la home o la sección de documentos).
2. La trabajadora accede al documento pendiente de firma en la sección Documentación laboral.
3. El sistema muestra el documento y el módulo de firma digital.
4. Si la trabajadora tiene una firma guardada, el sistema la ofrece como opción rápida. Si no, muestra el lienzo en blanco.
5. La trabajadora dibuja o confirma su firma.
6. La trabajadora confirma el envío de la firma.
7. El sistema registra la firma y marca el documento como firmado.

Estado de éxito: El documento queda firmado y desaparece de la lista de pendientes de firma.
Flujos alternativos:
- Si la trabajadora quiere redibujar su firma → puede borrarla y volver a trazar desde el lienzo antes de confirmar.

---

### Journey 5: Subir documento personal
Actor: Trabajadora (Hogar o SAD) | Objetivo: Añadir o actualizar un documento personal en su expediente

1. La trabajadora accede a la categoría Documentación personal en la sección de Documentos.
2. La trabajadora selecciona la opción de subir un nuevo documento o reemplazar uno existente.
3. El sistema solicita: tipo de documento, archivo (desde el dispositivo o cámara) y descripción opcional.
4. La trabajadora completa los datos y confirma.
5. El sistema sube el documento y lo incorpora al expediente de la trabajadora.

Estado de éxito: El documento aparece en la lista de Documentación personal. No es posible eliminar documentos personales subidos.
Flujos alternativos:
- Si el archivo supera el límite de tamaño o tiene un formato no admitido → el sistema informa a la trabajadora y no realiza la subida.

---

### Journey 6: Consultar estado del contrato (solo SAD)
Actor: Trabajadora SAD | Objetivo: Verificar los datos de su contrato laboral

1. La trabajadora accede a la sección de Perfil y navega a la subsección Contrato (visible solo en el perfil SAD).
2. El sistema muestra: tipo de contrato, fecha de inicio, número de empleada y un enlace para descargar el PDF del contrato.
3. La trabajadora puede descargar el PDF si necesita una copia.

Estado de éxito: La trabajadora visualiza la información de su contrato vigente. Los datos son de solo lectura.

---

### Journey 7: Flujo de completar perfil al aplicar a oferta (solo Hogar)
Actor: Trabajadora Hogar | Objetivo: Entender qué campos del perfil debe completar antes de poder aplicar

1. La trabajadora, con perfil incompleto, intenta aplicar a una oferta de trabajo.
2. El sistema detecta que el perfil no cumple los requisitos mínimos y muestra una advertencia informando de los campos obligatorios pendientes.
3. La advertencia incluye un acceso directo a la sección del perfil donde se encuentran esos campos.
4. La trabajadora completa los campos requeridos y regresa a la oferta para aplicar.

Estado de éxito: La trabajadora entiende qué campos le faltan y puede completarlos sin perder el contexto de la oferta.
Flujos alternativos: Ninguno relevante.

---

## Resultados y Éxito

La feature de gestión de perfil se considera completada cuando:

- La trabajadora puede ver su perfil completo organizado en secciones (Personal, Profesional, Educación, Idiomas, Contrato para SAD).
- La dirección de domicilio es editable; los datos core (nombre, apellidos, DNI/NIE) son de solo lectura con posibilidad de proponer cambios mediante documentación justificativa.
- La foto de perfil puede subirse, recortarse y actualizarse desde galería o cámara, y el cambio se refleja en toda la app.
- La sección de Documentos distingue claramente entre documentación personal (subible por la trabajadora, no eliminable) y laboral (solo lectura, descargable, firmable).
- La firma digital puede capturarse mediante lienzo táctil, guardarse en el perfil y reutilizarse para futuras firmas.
- El indicador de porcentaje de completitud del perfil es visible en la pantalla de perfil; en el perfil Hogar también desde la home.
- Las trabajadoras SAD pueden consultar el estado de su contrato y descargar el PDF.
- Las trabajadoras Hogar reciben una advertencia con los campos pendientes al intentar aplicar a una oferta con perfil incompleto.
- Los avisos de caducidad de documentos (DNI, certificados) llegan desde el servidor y son visibles en la sección de documentos.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Perfil — secciones y campos:**
- El perfil está organizado en secciones: Personal, Profesional, Educación, Idiomas. La sección Contrato solo es visible para trabajadoras SAD.
- Los datos core (nombre, apellidos, DNI/NIE, número de empleada) son siempre de solo lectura. No se ofrece un campo de edición directo para ellos.
- La dirección de domicilio es editable directamente desde la sección Personal.
- Los campos de cada sección se pueden editar mediante un botón de edición por sección (no hay un botón global de "editar perfil").
- Los cambios en una sección se guardan de forma individual al confirmar; no hay un botón global de "guardar todo el perfil".
- Los campos obligatorios se validan antes de guardar; si hay errores, se muestran mensajes en el campo correspondiente.

**Perfil — completitud (solo Hogar):**
- El porcentaje de completitud del perfil es visible en la pantalla de perfil de toda trabajadora Hogar y también en la home Hogar.
- Al intentar aplicar a una oferta con perfil incompleto, la app bloquea la acción y muestra una advertencia que lista los campos obligatorios pendientes con un acceso directo a completarlos.
- La trabajadora puede navegar libremente por el resto de la app con el perfil incompleto; el bloqueo solo ocurre en el momento de aplicar.

**Propuesta de cambio en DNI/NIE:**
- El DNI/NIE no es editable directamente. La app muestra la fecha de vencimiento del documento.
- La trabajadora puede iniciar un flujo de "proponer nueva fecha de vencimiento" adjuntando un documento justificativo. Este flujo envía la propuesta al backoffice para validación; el dato en la app no cambia hasta que el backoffice aprueba el cambio.

**Foto de perfil:**
- La foto de perfil es voluntaria; la app funciona correctamente sin ella.
- Al subir una nueva foto, la herramienta de recorte obliga a un formato cuadrado.
- El sistema optimiza automáticamente el tamaño de la imagen antes de subirla.
- Tamaño máximo permitido: 5 MB. Formatos admitidos: JPG, PNG.
- La foto actualizada aparece en todos los puntos de la app donde se muestra la imagen de la trabajadora.

**Documentos — reglas generales:**
- Los documentos se organizan en dos categorías: Documentación personal y Documentación laboral.
- La estructura de carpetas y tipos de documento dentro de cada categoría es configurable desde el backoffice (dinámica).
- Cualquier documento puede abrirse en el visor integrado de la app y descargarse.
- Los avisos de caducidad de DNI/certificados llegan desde el servidor; la trabajadora los ve en la sección de documentos y recibe un aviso en la home cuando hay documentos pendientes de firma.

**Documentos personales:**
- La trabajadora puede subir y reemplazar documentos personales. No puede eliminarlos.
- Al subir: debe seleccionar el tipo de documento, adjuntar el archivo (desde el dispositivo o cámara) y puede añadir una descripción opcional.
- Formatos admitidos: PDF, DOC, DOCX, JPG, PNG. Tamaño máximo: 10 MB. El sistema optimiza imágenes automáticamente.

**Documentos laborales:**
- La trabajadora no puede subir ni eliminar documentos laborales; su gestión es exclusiva del backoffice.
- La trabajadora puede consultar, descargar y firmar (cuando corresponda) documentos laborales.
- Cuando hay documentos pendientes de firma, se muestra un badge/aviso en la sección de documentos y en la home.

**Firma digital:**
- La firma se captura mediante un lienzo táctil en el que la trabajadora dibuja con el dedo.
- Antes de guardar, la trabajadora puede previsualizar la firma y borrarla para redibujarla.
- La firma se almacena como imagen en el perfil de la trabajadora y queda disponible para reutilizarla en firmas futuras.
- En cualquier momento, la trabajadora puede redibujar su firma desde el perfil.
- Al firmar un documento, si existe una firma guardada, el sistema la ofrece como opción rápida; la trabajadora puede optar por redibujar si lo prefiere.

**Estado del contrato (solo SAD):**
- La información del contrato es de solo lectura y está gestionada por el backoffice.
- Se muestra: tipo de contrato, fecha de inicio, número de empleada y un enlace para descargar el PDF del contrato.

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Home | Pulsar acceso rápido a Documentos | Pantalla de Documentos (ambas categorías unificadas) |
| Home | Badge/aviso de documento pendiente de firma | Pantalla de Documentos — sección Documentación laboral, documento pendiente resaltado |
| Perfil Hogar | Indicador de completitud | Pantalla de perfil con sección del campo pendiente activa |
| Advertencia de perfil incompleto (al aplicar a oferta) | Pulsar acceso directo a completar campos | Sección del perfil con los campos obligatorios pendientes |
| Documento laboral pendiente de firma | Pulsar "Firmar" | Módulo de firma digital con el documento como contexto |
| Sección Personal → DNI/NIE | Pulsar "Proponer cambio" | Flujo de propuesta de cambio con campo de nueva fecha y adjunto de documento justificativo |
| Módulo de firma | Confirmar firma | Regresa al documento firmado; el documento sale de la lista de pendientes |

---

## Criterios de Aceptación

### CA-001: Ver perfil organizado en secciones ← HU-001
GIVEN la trabajadora está autenticada en la app
WHEN accede a la sección "Mi Perfil"
THEN el sistema muestra el perfil con secciones: Personal (nombre, email, teléfono, dirección, fecha de nacimiento, DNI/NIE), Profesional (experiencia, especializaciones, certificaciones), Educación (títulos, cursos), Idiomas (idioma + nivel); para trabajadoras SAD aparece además la sección Contrato

### CA-002: Datos core de solo lectura y campos editables identificables ← HU-001
GIVEN la trabajadora está en la pantalla de perfil
WHEN visualiza cualquier sección
THEN los datos core (nombre, apellidos, DNI/NIE, número de empleada) se muestran sin botón de edición; los campos editables (dirección de domicilio, datos profesionales, idiomas) tienen un botón de edición visible a nivel de sección

### CA-003: Editar dirección de domicilio ← HU-002
GIVEN la trabajadora está en la sección Personal del perfil
WHEN pulsa el botón de edición de la sección y modifica la dirección de domicilio
THEN el sistema guarda el cambio, la nueva dirección se muestra en la sección Personal y el sistema confirma que el cambio se ha registrado

### CA-004: Validación de formato de teléfono ← HU-001
GIVEN la trabajadora está editando su información personal
WHEN introduce un número de teléfono con formato incorrecto y pulsa guardar
THEN el sistema muestra un mensaje de error en el campo de teléfono y no guarda los cambios hasta que el formato sea válido

### CA-005: Validación de formato de email ← HU-001
GIVEN la trabajadora está editando su información personal
WHEN introduce una dirección de email con formato incorrecto y pulsa guardar
THEN el sistema muestra un mensaje de error en el campo de email y no guarda los cambios hasta que el formato sea válido

### CA-006: Propuesta de cambio en DNI/NIE ← HU-004
GIVEN la trabajadora visualiza su sección Personal y tiene un DNI/NIE registrado con fecha de vencimiento
WHEN pulsa la opción "Proponer cambio" junto al campo DNI/NIE
THEN el sistema muestra un flujo en el que puede indicar la nueva fecha de vencimiento y adjuntar un documento justificativo; al confirmar, la propuesta queda enviada al backoffice y el dato en la app no se modifica hasta que el backoffice aprueba el cambio

### CA-007: Indicador de completitud del perfil en perfil y home (Hogar) ← HU-001
GIVEN la trabajadora Hogar está en la pantalla de perfil o en la home
WHEN el perfil tiene campos obligatorios sin completar
THEN se muestra el porcentaje de completitud del perfil de forma visible; en la home Hogar este indicador es visible para incentivar la cumplimentación

### CA-008: Mostrar foto de perfil actual o placeholder ← HU-003
GIVEN la trabajadora accede a su perfil
WHEN no tiene foto de perfil subida
THEN se muestra un placeholder genérico en lugar de la foto

### CA-009: Cambiar foto de perfil ← HU-003
GIVEN la trabajadora está en su perfil
WHEN pulsa sobre la foto de perfil (o el placeholder)
THEN el sistema ofrece dos opciones: elegir imagen de la galería del dispositivo o hacer una nueva foto con la cámara

### CA-010: Recortar y confirmar foto de perfil ← HU-003
GIVEN la trabajadora ha seleccionado una imagen para su foto de perfil
WHEN el sistema abre la herramienta de recorte
THEN la herramienta muestra la imagen con un marco de recorte de aspecto cuadrado que la trabajadora puede ajustar; al confirmar, el sistema optimiza la imagen y la sube mostrando el progreso de la operación

### CA-011: Límite de tamaño y formato para foto de perfil ← HU-003
GIVEN la trabajadora intenta subir una imagen para su foto de perfil
WHEN el archivo seleccionado supera los 5 MB o tiene un formato distinto a JPG o PNG
THEN el sistema informa a la trabajadora del motivo del rechazo y no inicia la subida

### CA-012: Actualización de la foto en toda la app ← HU-003
GIVEN la trabajadora ha subido una nueva foto de perfil con éxito
WHEN navega por cualquier sección de la app donde se muestre su imagen
THEN la nueva foto es visible en todos esos puntos sin necesidad de cerrar y reabrir la app

### CA-013: Ver documentos organizados en dos categorías ← HU-005, HU-006
GIVEN la trabajadora accede a la sección de Documentos (desde el perfil o desde la home)
WHEN la pantalla carga
THEN los documentos aparecen organizados en dos categorías: Documentación personal y Documentación laboral; dentro de cada categoría, la estructura de carpetas y tipos es la configurada por el backoffice

### CA-014: Abrir y descargar un documento ← HU-005, HU-006
GIVEN la trabajadora está en la sección de Documentos
WHEN pulsa sobre cualquier documento de cualquier categoría
THEN el sistema abre el documento en el visor integrado; la trabajadora puede descargarlo a su dispositivo desde el visor

### CA-015: Subir documento personal ← HU-005
GIVEN la trabajadora está en la categoría Documentación personal
WHEN selecciona la opción de subir un documento nuevo
THEN el sistema solicita: tipo de documento (de la lista configurable), archivo (del dispositivo o cámara) y descripción opcional; al confirmar, el documento queda registrado y visible en la categoría

### CA-016: Restricciones al subir documento personal ← HU-005
GIVEN la trabajadora intenta subir un documento personal
WHEN el archivo supera los 10 MB o tiene un formato distinto a PDF, DOC, DOCX, JPG o PNG
THEN el sistema informa a la trabajadora y no realiza la subida

### CA-017: No se pueden eliminar documentos personales ← HU-005
GIVEN la trabajadora está en la categoría Documentación personal
WHEN visualiza los documentos ya subidos
THEN no existe ninguna opción para eliminar documentos; solo la opción de reemplazar/actualizar un documento existente

### CA-018: Documentación laboral de solo lectura ← HU-006
GIVEN la trabajadora está en la categoría Documentación laboral
WHEN visualiza los documentos disponibles
THEN no existe ninguna opción para subir ni eliminar documentos laborales; solo están disponibles las acciones de consultar, descargar y firmar (cuando corresponda)

### CA-019: Badge de documentos pendientes de firma ← HU-006
GIVEN hay documentos laborales que requieren la firma de la trabajadora
WHEN la trabajadora abre la app o navega a la home o a la sección de Documentos
THEN se muestra un badge o aviso visible que indica que hay documentos pendientes de firma

### CA-020: Acceder a Documentos desde home ← HU-006
GIVEN la trabajadora está en la home
WHEN pulsa el acceso rápido a Documentos
THEN el sistema navega a la pantalla unificada de Documentos con ambas categorías (personal + laboral)

### CA-021: Mostrar lienzo de firma en blanco ← HU-007
GIVEN la trabajadora necesita firmar un documento o iniciar el flujo de firma desde su perfil
WHEN el sistema abre el módulo de firma digital
THEN se muestra un lienzo en blanco listo para capturar la firma táctil; si existe una firma previa guardada, el sistema la ofrece como opción rápida

### CA-022: Capturar firma táctil y previsualizar ← HU-007
GIVEN la trabajadora está en el lienzo de firma
WHEN dibuja su firma con el dedo en el lienzo
THEN el trazo queda registrado visualmente de forma fluida; la trabajadora puede previsualizar el resultado antes de confirmar

### CA-023: Borrar y redibujar firma ← HU-007
GIVEN la trabajadora está en el lienzo de firma y ha trazado una firma
WHEN pulsa el botón de borrar/reiniciar
THEN el lienzo vuelve a estar en blanco y la trabajadora puede volver a trazar su firma

### CA-024: Guardar y reutilizar firma ← HU-007
GIVEN la trabajadora confirma su firma en el lienzo
WHEN la firma se guarda
THEN queda almacenada como imagen en su perfil; en futuras firmas de documentos, el sistema ofrece la firma guardada como opción rápida para no tener que volver a dibujarla

### CA-025: Redibujar firma guardada ← HU-007
GIVEN la trabajadora tiene una firma guardada en su perfil
WHEN accede al módulo de firma desde su perfil
THEN el sistema muestra la firma actual y la opción de redibujarla; si confirma la acción, el lienzo queda en blanco para trazar la nueva firma

### CA-026: Firmar documento laboral pendiente ← HU-006, HU-007
GIVEN un documento laboral está pendiente de firma
WHEN la trabajadora accede al documento y confirma la firma (usando la guardada o dibujando una nueva)
THEN el sistema registra la firma, el documento queda marcado como firmado y desaparece de la lista de pendientes de firma

### CA-027: Bloqueo al aplicar a oferta con perfil incompleto (solo Hogar) ← HU-008
GIVEN la trabajadora Hogar tiene el perfil con campos obligatorios sin completar
WHEN intenta aplicar a una oferta de trabajo
THEN el sistema bloquea la acción y muestra una advertencia que lista los campos obligatorios pendientes con un acceso directo a la sección del perfil donde se encuentran

### CA-028: Navegación libre con perfil incompleto (solo Hogar) ← HU-008
GIVEN la trabajadora Hogar tiene el perfil incompleto
WHEN navega por cualquier sección de la app que no sea aplicar a una oferta
THEN puede hacerlo sin ningún bloqueo ni advertencia relacionada con el perfil incompleto

### CA-029: Ver estado del contrato (solo SAD) ← HU-009
GIVEN la trabajadora SAD accede a su perfil y navega a la sección Contrato
WHEN la pantalla carga
THEN el sistema muestra: tipo de contrato, fecha de inicio, número de empleada y un enlace para descargar el PDF del contrato; todos los datos son de solo lectura

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001]. La presentación del tipo de contrato puede diferir del valor real mostrado hasta que se resuelva la discrepancia con el backend. Responde el gap y ejecuta `/wf-spec-delta resolve` para completar.

### CA-030: Aviso de caducidad de documentos ← HU-005
GIVEN el servidor detecta que el DNI/NIE u otros certificados de la trabajadora están próximos a caducar o han caducado
WHEN la trabajadora abre la sección de Documentos
THEN el sistema muestra el aviso de caducidad asociado al documento correspondiente

---

## Checklist de Validación

- [x] Actores identificados (Trabajadora Hogar, Trabajadora SAD)
- [x] Flujos principales descritos paso a paso (7 journeys)
- [x] Estados de éxito definidos para cada journey
- [x] Edge cases documentados (perfil incompleto, formatos no admitidos, firma guardada vs. nueva, documento sin eliminar)
- [x] Estados de error definidos (validación de campos, rechazo por tamaño/formato)
- [x] Ambigüedades resueltas (excepto P-001 que requiere confirmación con backend)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance

- **Gestión de contraseñas y autenticación**: tratada en la feature `auth-and-onboarding` (F-001).
- **Gestión de disponibilidad**: la dirección de domicilio es editable en este spec, pero la gestión de los slots de disponibilidad horaria es responsabilidad de la feature `availability-management` (F-007).
- **Solicitud de ausencias**: fuera de este spec, gestionada en la feature `absence-management` (F-010).
- **Eliminación de documentos personales**: no está en el alcance por decisión de producto; solo se permite reemplazar.
- **Eliminación de la foto de perfil**: el PRD incluye el endpoint de borrado, pero no describe el flujo desde la app. Se excluye de este spec hasta aclaración; el flujo visible es subir/reemplazar.
- **Gestión de documentos laborales por parte de la trabajadora**: exclusiva del backoffice; la trabajadora solo consulta, descarga y firma.
- **Configuración de la estructura de carpetas de documentos**: es responsabilidad exclusiva del backoffice; la app la consume de forma dinámica.
- **Saldo de vacaciones y ausencias**: gestionado en `absence-management` (F-010), no en este spec.

---

## Items Pendientes

> Este spec tiene gaps **críticos** sin resolver. Las HUs afectadas están marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedará bloqueado hasta que se resuelvan.
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/wf-spec-validate profile-management_spec.md`.

### [P-001][CRÍTICO] Discrepancia en los valores del tipo de contrato entre spec y backend
- **Afecta**: [HU-009, CA-029]
- **Pregunta**: El PRD especifica que los tipos de contrato para trabajadoras SAD son "Indefinido" y "Fijo Discontinuo", pero el Swagger v1.6.0 devuelve `contract_type: "Tiempo completo" | "Tiempo parcial"`. ¿Son estos dos campos distintos (tipo jurídico vs. tipo de jornada) o el mismo campo con valores distintos? ¿Qué valores debe mostrar la app en la sección Contrato del perfil SAD?
- **Respuesta**: [CRÍTICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: El tipo de contrato mostrado en la sección Contrato del perfil SAD se presenta tal como lo devuelve el backend (`Tiempo completo` / `Tiempo parcial`) hasta que se resuelva el gap [P-001]. Esto es la asunción más conservadora para no inventar una lógica de traducción entre valores.

- **[A-002]**: La opción de eliminar la foto de perfil (que aparece como endpoint en el PRD pero sin flujo descrito en la app) se considera fuera de alcance de este spec. El flujo disponible en la app es exclusivamente subir/reemplazar la foto.

- **[A-003]**: La sección Contrato del perfil es solo visible para trabajadoras SAD. Las trabajadoras Hogar no tienen esta sección, ya que el PRD indica explícitamente que RF-9.5 aplica solo al perfil SAD.

- **[A-004]**: Los campos editables en la sección Profesional, Educación e Idiomas se pueden modificar directamente (añadir, editar, eliminar entradas) a diferencia de los datos core. Esta interpretación es consistente con los journeys anticipados en el discovery y la descripción de CA9 del PRD ("los campos del perfil pueden cambiar — nota en la UI para flexibilidad").
