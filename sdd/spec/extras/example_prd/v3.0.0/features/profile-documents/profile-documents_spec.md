# Spec: Perfil y Documentos

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-011

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades de empleo a traves de la app CUIDEO (tema azul) | Ver y editar perfil, subir foto de perfil, gestionar documentos personales, firmar documentos laborales |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Ver y editar perfil, subir foto de perfil, gestionar documentos personales, firmar documentos laborales, ver estado del contrato |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Configurar tipos de documento y carpetas, gestionar visibilidad de campos |
| Sistema | El propio sistema automatizado que ejecuta acciones programadas sin intervencion humana | Enviar notificaciones de caducidad de documentos |

---

## Historias de Usuario

### HU-032: Ver y editar perfil
Como trabajadora (Hogar o SAD)
quiero ver mi informacion personal y profesional y editar los campos permitidos
para que mi perfil este actualizado y completo.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-007]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-033: Estado del contrato (SAD)
Como trabajadora SAD
quiero ver la informacion de mi contrato actual
para que conozca mi tipo de contrato, fecha de inicio y pueda descargar el documento.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-010]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-034: Foto de perfil
Como trabajadora (Hogar o SAD)
quiero subir y actualizar mi foto de perfil
para que mi cuenta tenga una imagen personal identificable.

### HU-035: Gestion de documentos
Como trabajadora (Hogar o SAD)
quiero ver, subir y gestionar mis documentos personales y consultar la documentacion laboral
para que toda mi documentacion este accesible y pueda firmar los documentos que se requieran.

### HU-036: Firma digital
Como trabajadora (Hogar o SAD)
quiero capturar mi firma manuscrita en la pantalla
para que pueda firmar documentos y llamamientos de forma digital sin necesidad de papel.

---

## Recorridos de Usuario

### Journey 13: Gestionar documentos
Actor: Trabajadora (Hogar o SAD) | Objetivo: Consultar, subir y firmar documentos

1. La trabajadora accede a "Documentos" desde la home o el perfil.
2. La pantalla muestra dos categorias: Documentacion personal y Documentacion laboral (estructura de carpetas dinamica, configurable desde backoffice).
3. Para documentacion personal (DNI/NIE, certificados, etc.): la trabajadora puede subir y reemplazar documentos (formatos PDF, DOC, DOCX, JPG, PNG; maximo 10 MB; imagenes optimizadas automaticamente).
4. Para documentacion laboral (contrato, nominas, llamamientos firmados, etc.): solo puede consultar, descargar y firmar cuando corresponda. La gestion es exclusiva del backoffice.
5. Si hay documentos pendientes de firma: se muestra un aviso tanto en la seccion como en la home.
6. Si hay documentos proximos a caducar: el sistema envia avisos de caducidad.

Estado de exito: La trabajadora ha gestionado su documentacion personal y firmado los documentos laborales pendientes.

---

## Resultados y Exito

- **Documentos y perfil**: Las trabajadoras pueden gestionar su documentacion personal, firmar documentos laborales y mantener su perfil actualizado.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Documentacion personal**: La trabajadora puede subir y reemplazar documentos personales pero no eliminarlos. Formatos: PDF, DOC, DOCX, JPG, PNG. Maximo 10 MB. Imagenes optimizadas automaticamente.
- **Documentacion laboral**: Solo consulta, descarga y firma. La gestion es exclusiva del backoffice.
- **Estructura de documentos dinamica**: Las carpetas y tipos de documento son configurables desde backoffice.
- **Foto de perfil voluntaria**: La app funciona correctamente sin foto de perfil.
- **Porcentaje de completitud del perfil**: Visible en la pantalla principal del perfil y desde la home (Hogar).
- **Permiso de camara/archivos**: Se solicita solo en el momento en que se necesite (ej: al subir un documento o foto), no durante el onboarding.
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

---

## Criterios de Aceptacion

### CA-001: Perfil con secciones organizadas ← HU-032
GIVEN la trabajadora accede a su perfil
WHEN se carga la informacion
THEN se muestra organizada en secciones: Informacion Personal (nombre, email, telefono, direccion, fecha nacimiento, DNI/NIE), Profesional (experiencia, especializaciones, certificaciones), Educacion (titulos, cursos), Idiomas (idioma + nivel). Se muestra indicador de porcentaje de completitud del perfil

> ⚠ Parcial: La clasificacion de campos editables vs. solo-lectura vs. propuesta-de-cambio depende de la resolucion de gap P-007.

### CA-002: Direccion de domicilio editable ← HU-032
GIVEN la trabajadora esta en su perfil
WHEN accede al campo de direccion de domicilio
THEN puede editarlo directamente (ya que afecta a la zona de disponibilidad)

### CA-003: Vencimiento de DNI/NIE ← HU-032
GIVEN la trabajadora tiene un DNI/NIE con fecha de vencimiento
WHEN accede a su perfil
THEN ve la fecha de vencimiento y tiene acceso a un flujo de "proponer nueva fecha + adjuntar documento" (sin editar el dato existente; el backoffice valida)

### CA-004: Estado del contrato (SAD) ← HU-033
GIVEN la trabajadora SAD accede a la informacion de su contrato
WHEN se carga la pantalla
THEN se muestra: tipo de contrato, fecha de inicio, numero de empleada, enlace para descargar PDF del contrato. Informacion de solo lectura

> ⚠ Parcial: Los valores del tipo de contrato dependen de la resolucion de gap P-010 (Indefinido/Fijo Discontinuo vs. Tiempo completo/Tiempo parcial).

### CA-005: Foto de perfil ← HU-034
GIVEN la trabajadora accede a su foto de perfil
WHEN toca la foto o el placeholder
THEN puede elegir foto de galeria o hacer nueva foto. Puede recortar/redimensionar (aspecto cuadrado). La imagen se optimiza automaticamente (maximo 5 MB, formatos JPG/PNG). Se muestra progreso de subida. La foto se actualiza en toda la aplicacion inmediatamente

### CA-006: Documentos personales - subir y reemplazar ← HU-035
GIVEN la trabajadora accede a Documentacion Personal
WHEN quiere subir un documento
THEN puede seleccionar tipo, elegir archivo del dispositivo o hacer foto (formatos: PDF, DOC, DOCX, JPG, PNG; max 10 MB; imagenes optimizadas automaticamente). Puede reemplazar documentos existentes pero no eliminarlos

### CA-007: Documentos laborales - solo consulta y firma ← HU-035
GIVEN la trabajadora accede a Documentacion Laboral
WHEN consulta los documentos
THEN puede ver (visor de PDF en la app), descargar y firmar cuando corresponda. No puede subir ni eliminar. Indicador de documentos obligatorios y avisos de caducidad

### CA-008: Acceso a documentos desde home ← HU-035
GIVEN la trabajadora esta en el panel principal
WHEN toca el acceso a Documentos
THEN navega a la pantalla unificada con ambas categorias (personal + laboral)

### CA-009: Captura de firma digital ← HU-036
GIVEN la trabajadora accede al lienzo de firma
WHEN dibuja su firma con entrada tactil
THEN puede previsualizar la firma, borrarla y redibujarla. Al guardar, la firma se almacena en su perfil y puede reutilizarse para futuras firmas de documentos. Puede redibujar su firma en cualquier momento

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [ ] Ambiguedades resueltas — gaps P-007 y P-010 pendientes (campos editables, tipo de contrato)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- Gestion activa de pagos/nominas: fuera de alcance (el acceso de solo lectura a documentos de nomina SI esta incluido como parte de Documentacion laboral).
- Gestion de contrasenas desde la app (cambiar contrasena activa): el cambio de contrasena solo es posible via flujo de recuperacion de acceso.
