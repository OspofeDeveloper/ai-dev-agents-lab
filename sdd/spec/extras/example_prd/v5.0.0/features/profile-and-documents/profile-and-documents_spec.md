# Spec: Profile and Documents
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde /Users/oscar/Documents/AI_labs/Specs Test/project/prd-hogar-sad.md (scope: F-010 via prd-hogar-sad_discovery.md)
> Feature ID: F-010
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Profesional de cuidado a domicilio que busca oportunidades de empleo a traves de la app CUIDEO | Ver y editar perfil, subir foto, gestionar documentos personales, capturar firma digital, completar perfil para aplicar a ofertas |
| Trabajadora SAD | Profesional contratada del Servicio de Asistencia Social que gestiona sus servicios a traves de la app Felizvita | Ver y editar perfil, subir foto, gestionar documentos personales, consultar y firmar documentos laborales, capturar firma digital, consultar estado del contrato |

---

## Historias de Usuario

### HU-001: Ver y editar informacion del perfil
Como trabajadora (Hogar o SAD)
quiero ver mi informacion personal, profesional, educativa y de idiomas y editar los campos permitidos
para que mi perfil este actualizado y refleje correctamente mis datos y competencias

### HU-002: Gestionar foto de perfil
Como trabajadora (Hogar o SAD)
quiero subir, actualizar o ver mi foto de perfil
para que mi identidad visual este presente en la aplicacion

### HU-003: Consultar y gestionar documentos
Como trabajadora (Hogar o SAD)
quiero consultar mis documentos personales y laborales organizados por categorias, subir o reemplazar documentos personales y firmar documentos laborales cuando se requiera
para que mi documentacion este completa, actualizada y accesible

### HU-004: Capturar y reutilizar firma digital
Como trabajadora (Hogar o SAD)
quiero capturar mi firma manuscrita en la pantalla, guardarla y reutilizarla para futuras firmas de documentos
para que pueda firmar documentos laborales de forma rapida y sin repetir el proceso de captura

### HU-005: Consultar estado del contrato
Como trabajadora SAD
quiero ver la informacion de mi contrato actual (tipo, fecha de inicio, numero de empleada) y descargar el documento del contrato
para que pueda consultar mis condiciones laborales en cualquier momento

### HU-006: Completar perfil para aplicar a ofertas
Como trabajadora Hogar
quiero saber que campos de mi perfil estan pendientes y completarlos
para que pueda aplicar a ofertas de trabajo sin bloqueos

> **[INCOMPLETO]** — Pendiente de gap(s): [P-001]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

---

## Recorridos de Usuario

### Journey 1: Ver y editar informacion del perfil
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar y actualizar su informacion personal

1. La trabajadora accede a la seccion de Perfil desde el menu principal o desde un acceso directo en la home
2. La aplicacion muestra la informacion del perfil organizada en secciones: Informacion Personal, Profesional, Educacion, Idiomas
3. La trabajadora visualiza el indicador de porcentaje de completitud del perfil en la parte superior
4. La trabajadora selecciona una seccion para ver sus detalles
5. Los campos de solo lectura (nombre, apellidos, DNI/NIE) se muestran sin opcion de edicion
6. Para la direccion de domicilio (campo editable), la trabajadora pulsa el boton de edicion de la seccion, modifica el dato y guarda los cambios
7. Para informacion profesional (anos de experiencia, especializaciones, certificaciones), la trabajadora pulsa editar, realiza los cambios y guarda por seccion
8. Para idiomas, la trabajadora puede anadir un nuevo idioma con su nivel de competencia o eliminar uno existente
9. La aplicacion confirma que los cambios se han guardado correctamente

Estado de exito: La trabajadora ha consultado su perfil completo y los cambios realizados en campos editables se reflejan inmediatamente en la informacion mostrada.

Flujos alternativos:
- Si la trabajadora introduce un formato invalido en un campo editable (telefono, email) -> la aplicacion muestra un mensaje de error de validacion indicando el formato esperado y no guarda hasta que se corrija
- Si la trabajadora intenta editar un campo de solo lectura -> no hay opcion de edicion visible para esos campos

### Journey 2: Renovacion de DNI/NIE (propuesta de cambio)
Actor: Trabajadora (Hogar o SAD) | Objetivo: Actualizar la fecha de vencimiento de su DNI/NIE

1. La trabajadora accede a la seccion de Informacion Personal dentro de Perfil
2. La trabajadora localiza su numero de DNI/NIE y la fecha de vencimiento actual
3. La trabajadora selecciona la opcion de proponer un cambio en la fecha de vencimiento del DNI/NIE
4. La aplicacion solicita la nueva fecha de vencimiento y un documento justificativo (foto o archivo del nuevo DNI/NIE)
5. La trabajadora introduce la nueva fecha, adjunta el documento y envia la propuesta
6. La aplicacion confirma que la propuesta ha sido enviada y esta pendiente de validacion por el backoffice
7. La trabajadora recibe una notificacion (via mensaje del sistema) cuando la propuesta es aceptada o rechazada

Estado de exito: La propuesta de cambio de fecha de vencimiento del DNI/NIE se ha enviado correctamente y la trabajadora puede consultar su estado.

Flujos alternativos:
- Si la trabajadora no adjunta documento justificativo -> la aplicacion no permite enviar la propuesta e indica que el documento es obligatorio

### Journey 3: Subir o actualizar foto de perfil
Actor: Trabajadora (Hogar o SAD) | Objetivo: Establecer o cambiar su foto de perfil

1. La trabajadora accede a su perfil y ve su foto actual o un placeholder si no tiene foto
2. La trabajadora toca sobre la foto de perfil
3. La aplicacion ofrece dos opciones: elegir foto de la galeria o hacer una nueva foto con la camara
4. La trabajadora selecciona o captura una foto
5. La aplicacion muestra una vista de recorte con relacion de aspecto cuadrada para que la trabajadora ajuste el encuadre
6. La trabajadora confirma el recorte
7. La aplicacion comprime la imagen automaticamente, muestra un indicador de progreso de subida y actualiza la foto en toda la aplicacion

Estado de exito: La nueva foto de perfil se muestra en todas las pantallas donde aparece la imagen de la trabajadora.

Flujos alternativos:
- Si la imagen supera el tamano maximo aceptado (5MB antes de compresion) -> la aplicacion informa del limite y solicita otra imagen
- Si el formato no es compatible (solo JPG y PNG aceptados) -> la aplicacion informa de los formatos aceptados

### Journey 4: Consultar y gestionar documentos
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar documentos y subir documentacion personal

1. La trabajadora accede a la seccion de Documentos desde el perfil o desde un acceso directo en la home
2. La aplicacion muestra los documentos organizados en dos categorias: Documentacion personal y Documentacion laboral
3. Las carpetas y tipos de documento dentro de cada categoria son configurables desde backoffice (estructura dinamica)
4. **Documentacion personal**: la trabajadora puede ver los documentos existentes, subir nuevos documentos seleccionando tipo y archivo (PDF, DOC, DOCX, JPG, PNG; maximo 10MB), y reemplazar documentos existentes. No se permite eliminar documentos personales
5. **Documentacion laboral**: la trabajadora puede consultar documentos (contrato, nominas, llamamientos firmados), descargarlos y firmarlos cuando corresponda. No puede subir ni eliminar documentos laborales
6. La trabajadora toca un documento para verlo en un visor integrado, con opcion de descarga
7. Se muestran indicadores de documentos obligatorios pendientes y avisos de caducidad (DNI/certificados)

Estado de exito: La trabajadora ha consultado sus documentos, ha subido o reemplazado documentacion personal si lo necesitaba, y tiene visibilidad de documentos pendientes o proximos a caducar.

Flujos alternativos:
- Si el archivo a subir supera el tamano maximo (10MB) -> la aplicacion informa del limite
- Si el formato del archivo no es compatible -> la aplicacion informa de los formatos aceptados
- Si hay documentos pendientes de firma -> se muestra un badge/aviso en la seccion y en la home

### Journey 5: Capturar y reutilizar firma digital
Actor: Trabajadora (Hogar o SAD) | Objetivo: Registrar su firma manuscrita para usarla en firmas de documentos

1. La trabajadora accede a la funcionalidad de firma digital desde el perfil o desde el flujo de firma de un documento laboral
2. La aplicacion muestra un lienzo en blanco donde la trabajadora puede dibujar su firma con el dedo o un stylus
3. La trabajadora dibuja su firma
4. La trabajadora puede previsualizar la firma antes de guardarla
5. Si no queda conforme, pulsa el boton de borrar/reiniciar para volver a dibujar
6. La trabajadora confirma y guarda la firma
7. La firma queda almacenada en el perfil y esta disponible para reutilizarla en futuras firmas de documentos sin volver a dibujarla

Estado de exito: La firma digital esta guardada en el perfil de la trabajadora y se reutiliza automaticamente cuando firma un documento laboral.

Flujos alternativos:
- Si la trabajadora ya tiene una firma guardada y quiere cambiarla -> accede a la opcion de redibujar firma en cualquier momento, captura la nueva firma y reemplaza la anterior
- Si la trabajadora debe firmar un documento y no tiene firma guardada -> la aplicacion la dirige al flujo de captura de firma antes de completar la firma del documento

### Journey 6: Consultar estado del contrato (solo SAD)
Actor: Trabajadora SAD | Objetivo: Consultar la informacion de su contrato laboral

1. La trabajadora SAD accede a la seccion de contrato desde su perfil
2. La aplicacion muestra: tipo de contrato, fecha de inicio del contrato y numero de empleada
3. La trabajadora puede descargar el documento del contrato actual en formato PDF
4. Toda la informacion del contrato es de solo lectura (gestionada por el backoffice)

Estado de exito: La trabajadora SAD ha consultado la informacion de su contrato y ha podido descargar el documento si lo necesitaba.

Flujos alternativos:
- Si el contrato no esta disponible para descarga -> la aplicacion muestra un mensaje informativo indicando que el documento no esta disponible aun

> **[INCOMPLETO]** — Pendiente de gap(s): [P-001]. Los tipos de contrato mostrados dependen de la resolucion de la discrepancia entre PRD y Swagger.

### Journey 7: Completar perfil para aplicar a ofertas (solo Hogar)
Actor: Trabajadora Hogar | Objetivo: Completar los campos obligatorios del perfil para poder aplicar a ofertas

1. La trabajadora Hogar visualiza en la home el indicador de porcentaje de completitud de su perfil
2. Al intentar aplicar a una oferta con el perfil incompleto, la aplicacion muestra un aviso indicando los campos obligatorios pendientes con un acceso directo para completarlos
3. La trabajadora accede directamente a la seccion del perfil con los campos pendientes
4. La trabajadora completa los campos obligatorios y guarda los cambios
5. La aplicacion actualiza el porcentaje de completitud
6. La trabajadora vuelve a la oferta y puede completar la solicitud

Estado de exito: El perfil de la trabajadora Hogar cumple con los campos obligatorios minimos y ya no se bloquea la solicitud de ofertas.

Flujos alternativos:
- Si la trabajadora no completa todos los campos obligatorios y vuelve a intentar aplicar -> se sigue mostrando el bloqueo con los campos aun pendientes

---

## Resultados y Exito

La feature se considera exitosa cuando:

1. **Perfil consultable y editable**: La trabajadora puede ver toda su informacion personal, profesional, educativa y de idiomas organizada por secciones, y editar los campos permitidos (direccion, profesional, idiomas) con guardado por seccion
2. **Datos core protegidos**: Los campos de solo lectura (nombre, apellidos, DNI/NIE) no son editables directamente; solo el DNI/NIE permite una propuesta de cambio con documentacion justificativa
3. **Foto de perfil gestionable**: La trabajadora puede subir, recortar y actualizar su foto de perfil, que se refleja en toda la aplicacion
4. **Documentacion completa y accesible**: Los documentos personales se pueden subir y reemplazar; los documentos laborales se pueden consultar, descargar y firmar; la estructura de categorias es dinamica y configurable desde backoffice
5. **Firma digital disponible**: La firma manuscrita se captura una vez y se reutiliza para futuras firmas de documentos
6. **Contrato visible (SAD)**: La trabajadora SAD puede consultar tipo de contrato, fecha de inicio, numero de empleada y descargar el documento
7. **Perfil como habilitador (Hogar)**: La trabajadora Hogar ve su porcentaje de completitud y solo puede aplicar a ofertas cuando los campos obligatorios estan cumplimentados

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Campos de solo lectura vs editables**: nombre, apellidos, DNI/NIE, fecha de nacimiento y email son de solo lectura. La direccion de domicilio es editable porque afecta a la zona de disponibilidad. La informacion profesional (anos de experiencia, especializaciones, certificaciones), educacion y idiomas son editables
2. **Guardado por seccion**: los cambios se guardan al pulsar guardar dentro de la seccion editada, no de forma global para todo el perfil
3. **Propuesta de cambio de DNI/NIE**: solo el DNI/NIE permite enviar propuesta de cambio con documento adjunto. El resultado se notifica via mensaje del sistema. El resto de datos core solo se modifican desde backoffice sin intervencion de la trabajadora desde la app
4. **Foto de perfil voluntaria**: la aplicacion funciona correctamente sin foto de perfil, mostrando un placeholder. La foto se recorta a formato cuadrado antes de subir
5. **Compresion automatica de imagenes**: las imagenes (foto de perfil, documentos adjuntos) se comprimen automaticamente para no superar 1MB manteniendo calidad visual aceptable
6. **Documentacion personal vs laboral**: la documentacion personal permite subir y reemplazar (no eliminar); la documentacion laboral es de solo lectura (consultar, descargar, firmar). La gestion de documentos laborales es exclusiva del backoffice
7. **Estructura de documentos dinamica**: las carpetas y tipos de documento dentro de cada categoria son configurables desde backoffice
8. **Firma digital reutilizable**: la firma se captura una vez y se reutiliza. La trabajadora puede redibujar su firma en cualquier momento, reemplazando la anterior
9. **Indicador de completitud**: el porcentaje de completitud del perfil es visible en la pantalla principal del perfil y en la home (solo Hogar). El calculo depende de los campos obligatorios definidos
10. **Bloqueo de solicitudes con perfil incompleto (solo Hogar)**: al intentar aplicar a una oferta con perfil incompleto, se muestra advertencia con los campos pendientes y acceso directo a completarlos. La trabajadora puede navegar libremente por la app con perfil incompleto; el bloqueo solo aplica al momento de solicitar una oferta
11. **Avisos de caducidad**: la aplicacion muestra avisos para documentos proximos a caducar (DNI/certificados). Los avisos se generan desde el servidor
12. **Documentacion pendiente de firma**: se muestra un badge/aviso en la seccion de documentos y en la home cuando hay documentos laborales pendientes de firma
13. **Formatos aceptados para documentos**: PDF, DOC, DOCX, JPG, PNG con tamano maximo de 10MB por documento
14. **Formatos aceptados para foto de perfil**: JPG, PNG con tamano maximo de 5MB (antes de compresion)
15. **Estado del contrato (solo SAD)**: la informacion del contrato es de solo lectura. Se muestra tipo de contrato, fecha de inicio y numero de empleada

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home (Hogar) | Toca acceso directo de Perfil | Pantalla principal de Perfil con indicador de completitud |
| Home (SAD) | Toca acceso directo de Documentacion | Pantalla de Documentos (categorias personal + laboral) |
| Home (Hogar) | Toca indicador de completitud de perfil | Pantalla principal de Perfil |
| Perfil principal | Toca una seccion (Personal, Profesional, Educacion, Idiomas) | Detalle de la seccion seleccionada con opcion de edicion si aplica |
| Perfil principal | Toca foto de perfil | Opciones: elegir de galeria o hacer nueva foto |
| Perfil principal | Toca seccion de Documentos | Pantalla de Documentos (categorias personal + laboral) |
| Perfil principal | Toca seccion de Firma digital | Pantalla de firma (lienzo o previsualizacion de firma guardada) |
| Perfil principal (SAD) | Toca seccion de Contrato | Pantalla de estado del contrato |
| Documentos | Toca un documento | Visor del documento con opcion de descarga |
| Documentos | Toca subir documento personal | Selector de tipo + selector de archivo del dispositivo |
| Documentos | Toca firmar documento laboral | Flujo de firma (usa firma guardada o redirige a captura de firma si no tiene) |
| Oferta (Hogar) | Intenta aplicar con perfil incompleto | Aviso de bloqueo con lista de campos pendientes y enlace a Perfil |
| Notificacion de caducidad de documento | Toca la notificacion | Pantalla de Documentos |

---

## Criterios de Aceptacion

### CA-001: Visualizacion del perfil por secciones <- HU-001
GIVEN la trabajadora accede a la pantalla de Perfil
WHEN la pantalla se carga
THEN se muestra la informacion organizada en secciones: Informacion Personal (nombre, email, telefono, direccion de domicilio, fecha de nacimiento, DNI/NIE), Profesional (anos de experiencia, especializaciones, certificaciones), Educacion (titulos, cursos de formacion) e Idiomas (idioma y nivel de competencia)

### CA-002: Datos core de solo lectura <- HU-001
GIVEN la trabajadora esta en la pantalla de Perfil
WHEN visualiza los campos de nombre, apellidos, DNI/NIE, fecha de nacimiento y email
THEN estos campos se muestran sin opcion de edicion

### CA-003: Direccion de domicilio editable <- HU-001
GIVEN la trabajadora esta en la seccion de Informacion Personal
WHEN pulsa el boton de edicion de la seccion y modifica su direccion de domicilio
THEN la aplicacion guarda el cambio y actualiza la direccion mostrada

### CA-004: Editar informacion profesional <- HU-001
GIVEN la trabajadora esta en la seccion Profesional
WHEN pulsa editar, modifica los datos (anos de experiencia, especializaciones, certificaciones) y pulsa guardar
THEN los cambios se guardan para esa seccion y se reflejan inmediatamente

### CA-005: Gestionar idiomas <- HU-001
GIVEN la trabajadora esta en la seccion de Idiomas
WHEN anade un nuevo idioma con su nivel de competencia
THEN el idioma aparece en la lista de idiomas del perfil
Y WHEN elimina un idioma existente
THEN el idioma desaparece de la lista

### CA-006: Validacion de formato de telefono <- HU-001
GIVEN la trabajadora edita su numero de telefono
WHEN introduce un valor con formato invalido
THEN la aplicacion muestra un mensaje de error indicando el formato esperado y no permite guardar

### CA-007: Validacion de formato de email <- HU-001
GIVEN la trabajadora edita su email
WHEN introduce un valor con formato invalido
THEN la aplicacion muestra un mensaje de error indicando el formato esperado y no permite guardar

### CA-008: Indicador de porcentaje de completitud <- HU-001
GIVEN la trabajadora accede a la pantalla principal de Perfil
WHEN la pantalla se carga
THEN se muestra un indicador visible del porcentaje de completitud del perfil basado en los campos obligatorios cumplimentados

### CA-009: Propuesta de cambio de fecha de vencimiento del DNI/NIE <- HU-001
GIVEN la trabajadora esta en la seccion de Informacion Personal y su DNI/NIE tiene fecha de vencimiento
WHEN selecciona la opcion de proponer un cambio de fecha de vencimiento
THEN la aplicacion solicita la nueva fecha y un documento justificativo adjunto, sin permitir enviar si el documento no esta adjunto

### CA-010: Notificacion de resultado de propuesta de cambio <- HU-001
GIVEN la trabajadora ha enviado una propuesta de cambio de fecha de vencimiento del DNI/NIE
WHEN el backoffice acepta o rechaza la propuesta
THEN la trabajadora recibe un mensaje del sistema informando del resultado

### CA-011: Foto de perfil con placeholder <- HU-002
GIVEN la trabajadora no tiene foto de perfil subida
WHEN accede a la pantalla de Perfil
THEN se muestra un placeholder en lugar de la foto

### CA-012: Subir o cambiar foto de perfil <- HU-002
GIVEN la trabajadora toca sobre su foto de perfil (o el placeholder)
WHEN selecciona "Elegir de galeria" o "Hacer nueva foto"
THEN la aplicacion permite seleccionar o capturar una imagen

### CA-013: Recortar foto antes de subir <- HU-002
GIVEN la trabajadora ha seleccionado o capturado una foto
WHEN se muestra la vista de recorte
THEN la relacion de aspecto es cuadrada y la trabajadora puede ajustar el encuadre antes de confirmar

### CA-014: Compresion y progreso de subida de foto <- HU-002
GIVEN la trabajadora confirma el recorte de la foto
WHEN se inicia la subida
THEN la imagen se comprime automaticamente, se muestra un indicador de progreso, y al completarse la foto se actualiza en toda la aplicacion

### CA-015: Limite de tamano de foto de perfil <- HU-002
GIVEN la trabajadora selecciona una imagen para foto de perfil
WHEN la imagen supera 5MB
THEN la aplicacion informa del limite y solicita otra imagen

### CA-016: Formatos aceptados para foto <- HU-002
GIVEN la trabajadora selecciona un archivo para foto de perfil
WHEN el formato no es JPG ni PNG
THEN la aplicacion informa de los formatos aceptados

### CA-017: Documentos organizados en dos categorias <- HU-003
GIVEN la trabajadora accede a la pantalla de Documentos
WHEN la pantalla se carga
THEN se muestran los documentos organizados en dos categorias: Documentacion personal y Documentacion laboral, con carpetas y tipos configurables desde backoffice

### CA-018: Subir documento personal <- HU-003
GIVEN la trabajadora esta en la categoria de Documentacion personal
WHEN selecciona subir un nuevo documento, elige el tipo, selecciona un archivo del dispositivo (PDF, DOC, DOCX, JPG, PNG; maximo 10MB) y anade una descripcion opcional
THEN el documento se sube con compresion automatica de imagenes y aparece en la categoria correspondiente

### CA-019: Reemplazar documento personal <- HU-003
GIVEN la trabajadora tiene un documento personal subido previamente
WHEN selecciona reemplazarlo con un nuevo archivo
THEN el documento anterior se sustituye por el nuevo

### CA-020: No eliminar documentos personales <- HU-003
GIVEN la trabajadora esta en la categoria de Documentacion personal
WHEN consulta un documento subido
THEN no existe opcion de eliminar el documento, solo de reemplazarlo

### CA-021: Documentacion laboral de solo consulta <- HU-003
GIVEN la trabajadora esta en la categoria de Documentacion laboral
WHEN consulta los documentos (contrato, nominas, llamamientos firmados, etc.)
THEN puede ver, descargar y firmar los documentos cuando corresponda, pero no puede subir ni eliminar documentos laborales

### CA-022: Visor de documentos con descarga <- HU-003
GIVEN la trabajadora toca un documento en cualquier categoria
WHEN el documento se abre
THEN se muestra en un visor integrado con opcion de descarga

### CA-023: Avisos de caducidad de documentos <- HU-003
GIVEN un documento personal de la trabajadora (DNI/certificado) esta proximo a caducar
WHEN la trabajadora accede a la seccion de Documentos o recibe un aviso del servidor
THEN se muestra un indicador visible de caducidad proxima junto al documento afectado

### CA-024: Indicador de documentos obligatorios <- HU-003
GIVEN la trabajadora accede a la seccion de Documentos
WHEN hay documentos obligatorios que no se han subido
THEN se muestra un indicador de documentos obligatorios pendientes

### CA-025: Badge de documentacion pendiente de firma <- HU-003
GIVEN hay documentos laborales pendientes de firma de la trabajadora
WHEN la trabajadora accede a la seccion de Documentos o a la home
THEN se muestra un badge/aviso indicando que hay documentos pendientes de firma

### CA-026: Acceso rapido a Documentos desde home <- HU-003
GIVEN la trabajadora esta en la pantalla principal (home)
WHEN utiliza el acceso directo a Documentos
THEN accede a la pantalla unificada de Documentos con ambas categorias (personal + laboral)

### CA-027: Captura de firma en lienzo <- HU-004
GIVEN la trabajadora accede a la funcionalidad de firma digital
WHEN se muestra el lienzo de firma
THEN el lienzo esta en blanco y la trabajadora puede dibujar su firma con el dedo o un stylus

### CA-028: Borrar y reiniciar firma <- HU-004
GIVEN la trabajadora esta dibujando su firma en el lienzo
WHEN pulsa el boton de borrar/reiniciar
THEN el lienzo se limpia y puede volver a dibujar la firma

### CA-029: Previsualizar firma antes de guardar <- HU-004
GIVEN la trabajadora ha dibujado su firma
WHEN pulsa la opcion de previsualizar
THEN se muestra una previsualizacion de la firma antes de confirmar el guardado

### CA-030: Guardar firma en el perfil <- HU-004
GIVEN la trabajadora ha dibujado y previsualizado su firma
WHEN confirma el guardado
THEN la firma se almacena en su perfil y esta disponible para reutilizarla en futuras firmas de documentos

### CA-031: Reutilizar firma guardada <- HU-004
GIVEN la trabajadora tiene una firma guardada en su perfil
WHEN inicia el proceso de firma de un documento laboral
THEN la firma guardada se aplica automaticamente sin necesidad de volver a dibujarla

### CA-032: Redibujar firma en cualquier momento <- HU-004
GIVEN la trabajadora tiene una firma guardada
WHEN accede a la opcion de redibujar firma desde el perfil
THEN puede capturar una nueva firma que reemplaza la anterior

### CA-033: Firma requerida antes de firmar documento <- HU-004
GIVEN la trabajadora debe firmar un documento laboral y no tiene firma guardada
WHEN inicia el flujo de firma del documento
THEN la aplicacion la redirige al flujo de captura de firma antes de completar la firma del documento

### CA-034: Visualizacion del estado del contrato <- HU-005
GIVEN la trabajadora SAD accede a la seccion de contrato en su perfil
WHEN la pantalla se carga
THEN se muestra: tipo de contrato, fecha de inicio del contrato y numero de empleada, todo en modo solo lectura

> **[INCOMPLETO]** — Pendiente de gap(s): [P-001]. El tipo de contrato mostrado (Indefinido/Fijo Discontinuo vs Tiempo completo/Tiempo parcial) depende de la resolucion de la discrepancia entre PRD y Swagger.

### CA-035: Descargar documento del contrato <- HU-005
GIVEN la trabajadora SAD esta en la pantalla de estado del contrato
WHEN pulsa el enlace de descarga del contrato
THEN se descarga el documento del contrato actual en formato PDF

### CA-036: Bloqueo de solicitud de oferta con perfil incompleto <- HU-006
GIVEN la trabajadora Hogar tiene campos obligatorios del perfil sin cumplimentar
WHEN intenta aplicar a una oferta de trabajo
THEN la aplicacion muestra un aviso de bloqueo indicando los campos obligatorios pendientes con un acceso directo para ir a completarlos en el perfil

### CA-037: Completitud visible en home para Hogar <- HU-006
GIVEN la trabajadora Hogar accede a la pantalla principal (home)
WHEN la pantalla se carga
THEN se muestra el porcentaje de completitud del perfil de forma visible para incentivar su cumplimentacion

### CA-038: Navegacion libre con perfil incompleto <- HU-006
GIVEN la trabajadora Hogar tiene el perfil incompleto
WHEN navega por la aplicacion (consulta ofertas, disponibilidad, comunicacion, etc.)
THEN puede acceder a todas las funcionalidades sin restriccion, excepto al momento de aplicar a una oferta

---

## Checklist de Validacion

- [x] Actores identificados (Trabajadora Hogar y Trabajadora SAD con capacidades diferenciadas)
- [x] Flujos principales descritos paso a paso (7 journeys cubren todos los RFs del scope)
- [x] Estados de exito definidos para cada journey
- [x] Edge cases documentados (formatos invalidos, tamanos maximos, perfil incompleto, firma no guardada, documento no disponible)
- [x] Estados de error definidos (validaciones de formato, limites de tamano, bloqueo por perfil incompleto)
- [ ] Ambiguedades resueltas — **Pendiente**: [P-001] discrepancia tipo de contrato PRD vs Swagger
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- **Modificacion directa de datos core** (nombre, apellidos) desde la app: solo se gestionan desde backoffice. La unica excepcion es la propuesta de cambio de fecha de vencimiento del DNI/NIE con documento justificativo
- **Gestion de documentos laborales por la trabajadora**: la subida, edicion y eliminacion de documentos laborales es exclusiva del backoffice
- **Autenticacion biometrica** (Face ID, huella digital): fuera del alcance del MVP
- **Gestion activa de nominas/pagos**: la trabajadora solo consulta y descarga documentos de nomina como parte de la documentacion laboral
- **Funcionalidades de contrato para Hogar**: la seccion de estado del contrato es exclusiva del perfil SAD
- **Firma digital para documentos externos a la app**: la firma solo aplica a documentos laborales gestionados dentro de la plataforma

---

## Items Pendientes

> Este spec tiene gaps **criticos** sin resolver. Las HUs afectadas estan marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedara bloqueado hasta que se resuelvan.
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/wf-spec-validate <path>_spec.md`.

### [P-001][CRITICO] Tipo de contrato: discrepancia entre PRD y Swagger
- **Afecta**: [HU-005, HU-006]
- **Pregunta**: Los tipos de contrato "Indefinido / Fijo Discontinuo" del PRD y los valores "Tiempo completo / Tiempo parcial" del Swagger, son el mismo campo con nombres distintos o son dos dimensiones independientes del contrato? Si son dos dimensiones, la pantalla de contrato debe mostrar ambas (ej: "Indefinido + Tiempo completo") y las implicaciones para el bloqueo de perfil Hogar pueden cambiar.
- **Respuesta**: [CRITICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: Solo el DNI/NIE permite propuesta de cambio con documento adjunto. El resultado se notifica via mensaje del sistema. El resto de datos core (nombre, apellidos) solo se modifican desde backoffice sin intervencion de la trabajadora desde la app. (Basado en [P-018] del analysis — asuncion por defecto aplicada al no tener respuesta del cliente)
- **[A-002]**: Las imagenes (foto de perfil, documentos adjuntos) se comprimen automaticamente para no superar 1MB manteniendo calidad visual aceptable. El tamano exacto se ajustara en el Plan segun las capacidades del dispositivo y la velocidad de red tipica. (Basado en [P-015] del analysis — asuncion por defecto aplicada al no tener respuesta del cliente)

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-04-05 | Generacion inicial via fast-track (scope F-010 desde discovery) |
