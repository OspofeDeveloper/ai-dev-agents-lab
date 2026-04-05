# Spec: Perfil
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-009

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo | Ver y editar perfil, subir foto, gestionar documentos personales, capturar firma digital, ver porcentaje de completitud |
| Trabajadora SAD | Trabajadora del Servicio de Asistencia Social | Ver y editar perfil, subir foto, gestionar documentos personales, consultar documentacion laboral, firmar documentos, capturar firma digital, ver estado del contrato |

---

## Historias de Usuario

### HU-001: Ver y editar perfil
Como trabajadora (Hogar o SAD)
quiero ver mi informacion personal y profesional y editar los campos permitidos
para que mis datos esten actualizados.

### HU-002: Gestionar foto de perfil
Como trabajadora (Hogar o SAD)
quiero subir y actualizar mi foto de perfil
para que mi perfil sea identificable.

### HU-003: Gestionar documentos
Como trabajadora (Hogar o SAD)
quiero ver, subir y gestionar mis documentos (personales y laborales)
para que mi documentacion este al dia y pueda firmar cuando sea necesario.

### HU-004: Capturar firma digital
Como trabajadora (Hogar o SAD)
quiero capturar y almacenar mi firma manuscrita
para que pueda usarla para firmar documentos desde la app.

### HU-005: Ver estado del contrato (SAD)
Como trabajadora SAD
quiero ver la informacion de mi contrato actual
para que conozca mi tipo de contrato, fecha de inicio y numero de empleada.

### HU-006: Completar perfil para aplicar a ofertas (Hogar)
Como trabajadora Hogar
quiero saber que campos de mi perfil estan pendientes
para que pueda completarlos antes de aplicar a ofertas.

---

## Recorridos de Usuario

### Journey 1: Consultar y editar perfil
Actor: Trabajadora (Hogar o SAD) | Objetivo: Actualizar su informacion
1. La trabajadora accede a "Perfil" desde el home o menu.
2. Ve su informacion organizada en secciones: Informacion Personal, Profesional, Educacion, Idiomas, y Contrato (solo SAD).
3. Ve un indicador de porcentaje de completitud del perfil.
4. Los datos core (nombre, apellidos, DNI/NIE, etc.) son de solo lectura.
5. La direccion de domicilio es editable (afecta a la zona de disponibilidad).
6. Para los campos editables, pulsa el boton de edicion por seccion, modifica los datos y guarda.
7. Para DNI/NIE: ve la fecha de vencimiento y puede proponer nueva fecha adjuntando documento (sin editar el dato existente; el backoffice valida el cambio).

Estado de exito: Los datos editados quedan guardados y el perfil refleja la informacion actualizada.
Flujos alternativos:
- Validaciones de formato para telefono, email y DNI/NIE.
- Si un campo obligatorio esta vacio, se muestra error.

### Journey 2: Subir foto de perfil
Actor: Trabajadora (Hogar o SAD) | Objetivo: Actualizar su foto
1. La trabajadora toca su foto de perfil (o placeholder si no tiene).
2. Elige entre galeria o camara.
3. Recorta/redimensiona la foto (relacion de aspecto cuadrada).
4. La foto se comprime automaticamente (max 5MB, JPG o PNG).
5. Ve progreso de subida.
6. La foto se actualiza en toda la aplicacion inmediatamente.

Estado de exito: La foto de perfil queda actualizada en todo el sistema.

### Journey 3: Gestionar documentos
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar y gestionar su documentacion
1. La trabajadora accede a "Documentos" (desde el perfil o desde la home, donde hay acceso rapido especialmente para nominas).
2. Ve documentos organizados en dos categorias: Documentacion personal y Documentacion laboral.
3. Las carpetas y tipos de documento dentro de cada categoria son configurables desde backoffice (estructura dinamica).
4. Toca un documento para verlo (visor integrado, opcion de descarga).
5. Para documentacion personal: puede subir y reemplazar documentos (seleccionar tipo, elegir archivo del dispositivo o hacer foto; formatos: PDF, DOC, DOCX, JPG, PNG; max 10MB; compresion automatica). No puede eliminar documentos personales.
6. Para documentacion laboral: solo puede consultar, descargar y firmar. No puede subir ni eliminar (gestion exclusiva del backoffice).
7. Recibe avisos de caducidad para DNI/certificados desde servidor.
8. Ve indicador de documentos obligatorios.
9. Ve badge/aviso para documentacion pendiente de firma.

Estado de exito: La trabajadora puede consultar toda su documentacion y mantener actualizada la documentacion personal.

### Journey 4: Capturar firma digital
Actor: Trabajadora (Hogar o SAD) | Objetivo: Registrar su firma manuscrita
1. La trabajadora accede a la seccion de firma digital.
2. Ve un lienzo de firma en blanco.
3. Dibuja su firma con el dedo o stylus.
4. Puede borrar/reiniciar si no queda satisfecha.
5. Previsualiza la firma antes de guardar.
6. Guarda la firma (almacenada como PNG).
7. La firma queda disponible para futuras firmas de documentos.
8. Puede redibujar la firma en cualquier momento.

Estado de exito: La firma queda almacenada y disponible para usar en firmas de documentos.

### Journey 5: Consultar estado del contrato (SAD)
Actor: Trabajadora SAD | Objetivo: Ver informacion de su contrato
1. La trabajadora accede a la seccion de contrato en su perfil.
2. Ve tipo de contrato (Indefinido, Fijo Discontinuo), fecha de inicio y numero de empleada.
3. Puede descargar el PDF del contrato actual.
4. La informacion es de solo lectura.

Estado de exito: La trabajadora puede consultar y descargar su contrato.

---

## Resultados y Exito

- Cada trabajadora puede mantener su perfil actualizado dentro de los campos permitidos.
- La documentacion personal se gestiona de forma autonoma; la laboral es de solo lectura con opcion de firma.
- La firma digital queda almacenada y reutilizable.
- La trabajadora Hogar sabe que campos le faltan para aplicar a ofertas.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- Las secciones del perfil son: Informacion Personal (nombre, email, telefono, direccion de domicilio, fecha de nacimiento, DNI/NIE), Profesional (anos de experiencia, especializaciones, certificaciones), Educacion (titulos, cursos), Idiomas (idioma + nivel), Contrato (solo SAD: tipo, fecha inicio).
- Los datos core (nombre, apellidos, DNI/NIE, etc.) son de solo lectura. La direccion de domicilio es editable.
- Para DNI/NIE: se muestra la fecha de vencimiento y existe un flujo de "proponer nueva fecha + adjuntar documento" (sin editar el dato directamente; el backoffice valida).
- Los campos del perfil pueden cambiar (nota en la UI para flexibilidad).
- El guardado es por seccion, no global.
- La foto de perfil es voluntaria; la app funciona sin ella.
- Foto: max 5MB, formatos JPG/PNG, recorte cuadrado, compresion automatica.
- Documentos personales: se pueden subir y reemplazar, no eliminar. Formatos: PDF, DOC, DOCX, JPG, PNG; max 10MB; compresion automatica de imagenes.
- Documentos laborales: solo consultar, descargar y firmar. No subir ni eliminar.
- Las carpetas y tipos de documento son configurables desde backoffice (estructura dinamica).
- La firma se almacena como PNG y se reutiliza para futuras firmas.
- (Solo Hogar) Porcentaje de completitud del perfil visible desde la home. Al intentar aplicar a una oferta con perfil incompleto, se muestra advertencia con acceso directo a completar campos obligatorios.
- (Solo SAD) El tipo de contrato esperado es Indefinido o Fijo Discontinuo. El Swagger v1.6.0 devuelve "Tiempo completo" / "Tiempo parcial", lo cual esta pendiente de alinear con backend.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Home | Tocar "Perfil" | Pantalla principal del perfil |
| Home | Tocar "Documentacion" | Pantalla de documentos (ambas categorias) |
| Perfil | Tocar seccion editable | Formulario de edicion de la seccion |
| Perfil | Tocar foto | Selector de foto (galeria / camara) |
| Perfil | Tocar "Documentos" | Pantalla de documentos |
| Perfil | Tocar "Contrato" (SAD) | Detalle del contrato |
| Perfil | Tocar "Firma" | Lienzo de firma digital |
| Documentos | Tocar documento | Visor de documento (con opcion de descarga) |
| Documentos | Firmar documento laboral | Proceso de firma con firma almacenada |

---

## Criterios de Aceptacion

### CA-001: Perfil organizado en secciones <- HU-001
GIVEN la trabajadora accede a su perfil
WHEN se carga la pantalla
THEN ve su informacion organizada en secciones: Informacion Personal, Profesional, Educacion, Idiomas, y Contrato (solo SAD).

### CA-002: Datos core solo lectura <- HU-001
GIVEN la trabajadora ve su perfil
WHEN revisa los datos core (nombre, apellidos, DNI/NIE)
THEN estos campos son de solo lectura; la direccion de domicilio es editable.

### CA-003: Edicion por seccion <- HU-001
GIVEN la trabajadora quiere editar un campo permitido
WHEN pulsa el boton de edicion en la seccion correspondiente
THEN puede modificar y guardar los cambios por seccion.

### CA-004: Validaciones de formato <- HU-001
GIVEN la trabajadora esta editando su perfil
WHEN modifica telefono, email o DNI/NIE
THEN se aplican validaciones de formato especificas para cada campo.

### CA-005: Campos obligatorios <- HU-001
GIVEN la trabajadora esta editando su perfil
WHEN deja un campo obligatorio vacio
THEN se muestra error de validacion.

### CA-006: Porcentaje de completitud <- HU-001
GIVEN la trabajadora accede a su perfil
WHEN se carga la pantalla
THEN se muestra un indicador de porcentaje de completitud del perfil.

### CA-007: DNI/NIE con vencimiento <- HU-001
GIVEN la trabajadora ve la seccion de DNI/NIE en su perfil
WHEN consulta el campo
THEN se muestra la fecha de vencimiento y puede proponer nueva fecha adjuntando documento (sin editar el dato existente).

### CA-008: Foto actual o placeholder <- HU-002
GIVEN la trabajadora accede a su perfil
WHEN se carga la foto
THEN se muestra la foto de perfil actual o un placeholder si no tiene.

### CA-009: Elegir origen de foto <- HU-002
GIVEN la trabajadora quiere cambiar su foto
WHEN toca la foto
THEN puede elegir entre galeria o camara.

### CA-010: Recorte cuadrado <- HU-002
GIVEN la trabajadora ha seleccionado una foto
WHEN se muestra la herramienta de edicion
THEN puede recortar/redimensionar con relacion de aspecto cuadrada.

### CA-011: Compresion y limites <- HU-002
GIVEN la trabajadora confirma la foto
WHEN se prepara para subida
THEN se comprime automaticamente, max 5MB, formatos JPG/PNG.

### CA-012: Progreso de subida <- HU-002
GIVEN la trabajadora esta subiendo su foto
WHEN la subida esta en curso
THEN se muestra progreso de subida.

### CA-013: Actualizacion inmediata <- HU-002
GIVEN la trabajadora ha subido su foto
WHEN se completa la subida
THEN la foto se actualiza en toda la aplicacion inmediatamente.

### CA-014: Documentos en dos categorias <- HU-003
GIVEN la trabajadora accede a Documentos
WHEN se carga la pantalla
THEN se muestran organizados en Documentacion personal y Documentacion laboral.

### CA-015: Estructura dinamica <- HU-003
GIVEN la trabajadora ve la pantalla de documentos
WHEN consulta las carpetas
THEN las carpetas y tipos de documento son configurables desde backoffice (estructura dinamica).

### CA-016: Visor de documentos <- HU-003
GIVEN la trabajadora quiere ver un documento
WHEN toca el documento
THEN se abre el visor integrado con opcion de descarga.

### CA-017: Subir documento personal <- HU-003
GIVEN la trabajadora esta en documentacion personal
WHEN decide subir o reemplazar un documento
THEN puede seleccionar tipo, elegir archivo o hacer foto; formatos: PDF, DOC, DOCX, JPG, PNG; max 10MB; compresion automatica de imagenes. No puede eliminar documentos personales.

### CA-018: Documentacion laboral solo lectura <- HU-003
GIVEN la trabajadora esta en documentacion laboral
WHEN revisa las opciones
THEN solo puede consultar, descargar y firmar. No puede subir ni eliminar.

### CA-019: Acceso desde home <- HU-003
GIVEN la trabajadora quiere acceder a documentos
WHEN esta en la home
THEN hay acceso rapido a Documentos (especialmente nominas). El acceso conduce a pantalla unificada con ambas categorias.

### CA-020: Avisos de caducidad <- HU-003
GIVEN un documento de la trabajadora esta proximo a caducar
WHEN faltan 30 dias o menos
THEN recibe aviso de caducidad desde servidor.

### CA-021: Indicador documentos obligatorios <- HU-003
GIVEN la trabajadora accede a Documentos
WHEN se carga la pantalla
THEN se muestra indicador de documentos obligatorios.

### CA-022: Badge documentacion pendiente firma <- HU-003
GIVEN la trabajadora tiene documentos pendientes de firma
WHEN accede a Documentos o a la home
THEN se muestra badge/aviso para documentacion pendiente de firma.

### CA-023: Lienzo de firma <- HU-004
GIVEN la trabajadora accede a la seccion de firma digital
WHEN se carga la pantalla
THEN ve un lienzo de firma en blanco.

### CA-024: Captura tactil <- HU-004
GIVEN la trabajadora esta en el lienzo de firma
WHEN dibuja con el dedo o stylus
THEN se captura la entrada para la firma.

### CA-025: Borrar y reiniciar firma <- HU-004
GIVEN la trabajadora esta dibujando su firma
WHEN quiere reiniciar
THEN puede borrar/reiniciar la firma.

### CA-026: Previsualizacion de firma <- HU-004
GIVEN la trabajadora ha dibujado su firma
WHEN quiere confirmar
THEN puede previsualizar la firma antes de guardar.

### CA-027: Guardar firma como PNG <- HU-004
GIVEN la trabajadora confirma su firma
WHEN guarda
THEN la firma se almacena como archivo PNG, asociada al perfil.

### CA-028: Reutilizar firma <- HU-004
GIVEN la trabajadora tiene una firma almacenada
WHEN necesita firmar un documento
THEN se usa la firma guardada.

### CA-029: Redibujar firma <- HU-004
GIVEN la trabajadora tiene una firma almacenada
WHEN decide cambiarla
THEN puede redibujar la firma en cualquier momento.

### CA-030: Tipo de contrato <- HU-005
GIVEN la trabajadora SAD accede a la seccion de contrato
WHEN se carga la informacion
THEN se muestra el tipo de contrato: Indefinido o Fijo Discontinuo.

### CA-031: Fecha inicio y numero empleada <- HU-005
GIVEN la trabajadora SAD accede a la seccion de contrato
WHEN se carga la informacion
THEN se muestra la fecha de inicio del contrato y el numero de empleada.

### CA-032: Descarga PDF contrato <- HU-005
GIVEN la trabajadora SAD accede a la seccion de contrato
WHEN quiere descargar el contrato
THEN puede descargar el PDF del contrato actual.

### CA-033: Contrato solo lectura <- HU-005
GIVEN la trabajadora SAD ve la informacion del contrato
WHEN revisa las opciones
THEN la informacion es de solo lectura (gestionada por admin).

### CA-034: Completitud visible desde home Hogar <- HU-006
GIVEN la trabajadora Hogar esta en la home
WHEN se carga la pantalla
THEN el porcentaje de completitud del perfil es visible para incentivar su cumplimentacion.

### CA-035: Bloqueo al aplicar con perfil incompleto <- HU-006
GIVEN la trabajadora Hogar tiene el perfil incompleto
WHEN intenta aplicar a una oferta
THEN se muestra advertencia informando de los campos obligatorios pendientes, con acceso directo a completarlos.

---

## Checklist de Validacion
- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [x] Ambiguedades resueltas
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance
- Edicion directa de datos core (nombre, apellidos, DNI/NIE) — solo propuesta de cambio para backoffice
- Eliminacion de documentos personales (solo reemplazo)
- Subida de documentos laborales (gestion exclusiva del backoffice)
- Gestion de contrasena desde el perfil (se gestiona en F-001 Autenticacion)
- Funciones sociales (valoraciones, perfiles publicos)

---

## Asunciones Aplicadas
| Gap origen | Asuncion aplicada |
|------------|-------------------|
| [P-008] | El tipo de contrato esperado es "Indefinido" o "Fijo Discontinuo". El Swagger devuelve "Tiempo completo" / "Tiempo parcial"; se asume que son dimensiones distintas y ambos deben mostrarse cuando se alinee con backend |
