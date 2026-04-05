# Spec: Profile
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-009

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades. Usa la app CUIDEO (identidad visual azul). | Ver y editar perfil personal y profesional, gestionar foto de perfil, subir y reemplazar documentación personal, firmar documentación laboral, ver indicador de completitud. |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Ver y editar perfil personal y profesional, gestionar foto de perfil, subir y reemplazar documentación personal, firmar documentación laboral, consultar estado del contrato. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Subir documentación laboral, validar propuesta de cambio de DNI/NIE, configurar carpetas y tipos de documentos. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-022: Ver y editar mi perfil
Como trabajadora (Hogar o SAD) / quiero consultar mi información personal y profesional, y editar los campos que me corresponden / para que mi perfil esté actualizado y refleje mi situación real.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-006]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-023: Gestionar mi foto de perfil
Como trabajadora (Hogar o SAD) / quiero subir o cambiar mi foto de perfil / para que mis coordinadoras puedan identificarme fácilmente.

### HU-024: Gestionar mis documentos (subir y firmar)
Como trabajadora (Hogar o SAD) / quiero consultar, subir y firmar mis documentos personales y laborales desde la app / para que toda mi documentación esté disponible y al día.

### HU-025: Ver el estado de mi contrato (SAD)
Como trabajadora SAD / quiero consultar los datos de mi contrato actual / para que pueda conocer mi tipo de contrato, fecha de inicio y número de empleada.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-006]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

---

## Recorridos de Usuario

### Journey 1: Editar perfil y completar información
Actor: Trabajadora Hogar o SAD | Objetivo: Actualizar datos personales y profesionales

1. La trabajadora accede a la sección de Perfil.
2. La pantalla muestra las secciones: Información Personal, Profesional, Educación, Idiomas e indicador de completitud.
3. La trabajadora toca el botón de edición de la sección que desea actualizar.
4. Modifica los campos editables (la dirección de domicilio, campos profesionales, idiomas, etc.).
5. Los datos core (nombre, apellidos, DNI/NIE) aparecen en modo solo lectura.
6. Guarda los cambios. Los cambios se reflejan inmediatamente en la app.

Estado de éxito: Los cambios guardados se reflejan inmediatamente. El indicador de completitud aumenta al añadir información (perfil Hogar).

Flujos alternativos:
- Para proponer cambio de fecha de DNI/NIE → se muestra el flujo de "proponer nueva fecha + adjuntar documento" que el backoffice valida.

---

## Resultados y Éxito

- **Perfil actualizado**: Los cambios guardados se reflejan inmediatamente en la app. El porcentaje de completitud aumenta al añadir información (perfil Hogar).
- **Documentación gestionada**: Los documentos subidos quedan disponibles en su categoría. Los documentos laborales pendientes de firma muestran badge de alerta.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Perfil:**
- Los datos core del perfil (nombre, apellidos, DNI/NIE) son de solo lectura.
- La dirección de domicilio es editable.
- Para el DNI/NIE: se muestra la fecha de vencimiento y existe un flujo para "proponer nueva fecha + adjuntar documento" que el backoffice valida; la trabajadora no edita el dato existente directamente.
- [PENDIENTE P-006]: qué tipo(s) de contrato se muestran en el perfil SAD y en "Estado del contrato" (dimensión jurídica: Indefinido/Fijo Discontinuo; dimensión de jornada: Tiempo completo/Tiempo parcial; o ambas).

**Completitud del perfil (Hogar):**
- Al intentar aplicar a una oferta con perfil incompleto, se muestra una advertencia o bloqueo informando de los campos obligatorios pendientes, con acceso directo a completarlos.
- [P-013 — asunción aplicada]: El porcentaje de completitud computa los campos de Información Personal, Profesional e Idiomas. La foto de perfil suma al porcentaje pero es opcional. El indicador visible en home solo aplica al perfil Hogar.

**Documentos:**
- Documentación personal (DNI/NIE, certificados, etc.): la trabajadora puede subir y reemplazar pero no eliminar.
- Documentación laboral (contrato, nóminas, etc.): la trabajadora puede consultar, descargar y firmar; no puede subir ni eliminar.
- Los documentos pendientes de firma generan badge/aviso en la sección de Documentos y en la home.

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.
- La trabajadora puede adjuntar fotos y documentos. El sistema informa si un archivo no puede enviarse antes de intentar la subida.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Oferta (detalle) | Pulsa "Aplicar" (perfil incompleto — Hogar) | Advertencia con campos pendientes y acceso a completar perfil |

---

## Criterios de Aceptación

### CA-001: Ver perfil — secciones y campos ← HU-022
GIVEN la trabajadora accede a su perfil
WHEN la pantalla se carga
THEN se muestran las secciones: Información Personal (nombre, email, teléfono, dirección — editable, fecha de nacimiento, DNI/NIE), Profesional (experiencia, especializaciones, certificaciones), Educación (títulos, cursos), Idiomas (idioma + nivel); se muestra el indicador de porcentaje de completitud del perfil.

---

### CA-002: Ver perfil — datos core de solo lectura; dirección editable ← HU-022
GIVEN la trabajadora está en la pantalla de perfil
WHEN revisa los campos
THEN los datos core (nombre, apellidos, DNI/NIE) son de solo lectura; la dirección de domicilio tiene botón de edición; los demás campos editables tienen botón de edición por sección.

---

### CA-003: Ver perfil — DNI/NIE con fecha de vencimiento y propuesta de cambio ← HU-022
GIVEN la trabajadora está en la pantalla de perfil, sección DNI/NIE
WHEN revisa el campo
THEN se muestra la fecha de vencimiento del DNI/NIE; hay un flujo para "proponer nueva fecha + adjuntar documento" que el backoffice valida; la trabajadora no puede editar el dato directamente.

---

### CA-004: Ver perfil — tipo de contrato SAD (pendiente) ← HU-022

> [INCOMPLETO] — Pendiente de gap [P-006]: qué tipo(s) de contrato se muestran en el perfil SAD (dimensión jurídica, de jornada, o ambas) no está definido.

---

### CA-005: Perfil Hogar — advertencia al aplicar con perfil incompleto ← HU-022
GIVEN la trabajadora Hogar tiene campos obligatorios del perfil sin completar
WHEN intenta aplicar a una oferta
THEN la app muestra una advertencia o bloqueo informando de los campos obligatorios pendientes, con acceso directo a completarlos.

---

### CA-006: Foto de perfil — subir y cambiar ← HU-023
GIVEN la trabajadora está en la pantalla de foto de perfil
WHEN toca la foto o el placeholder
THEN puede elegir foto de galería o hacer una nueva foto; puede recortarla en relación de aspecto cuadrada antes de subir; la app muestra el progreso de subida; la nueva foto se refleja en toda la app inmediatamente.

---

### CA-007: Documentos — lista por categorías ← HU-024
GIVEN la trabajadora accede a la sección de documentos
WHEN la pantalla se carga
THEN se muestran los documentos organizados en dos categorías: Documentación personal y Documentación laboral; las carpetas y tipos dentro de cada categoría son configurables desde backoffice.

---

### CA-008: Documentos personales — subir y reemplazar ← HU-024
GIVEN la trabajadora está en la sección de documentación personal
WHEN sube o reemplaza un documento
THEN puede seleccionar el tipo, elegir un archivo del dispositivo o hacer una foto (formatos: PDF, DOC, DOCX, JPG, PNG), añadir descripción opcional; el documento queda disponible en la app. No puede eliminar documentos personales, solo reemplazar.

---

### CA-009: Documentos laborales — solo lectura y firma ← HU-024
GIVEN la trabajadora está en la sección de documentación laboral
WHEN revisa sus documentos laborales
THEN puede consultar y descargar los documentos; no puede subir ni eliminar documentos laborales; si un documento requiere firma, puede firmarlo digitalmente; los documentos pendientes de firma generan badge/aviso en la sección y en la home.

---

### CA-010: Firma digital — captura y almacenamiento ← HU-024
GIVEN la trabajadora accede al lienzo de firma digital
WHEN dibuja su firma con el dedo o stylus
THEN puede borrar/reiniciar la firma, previsualizar antes de guardar, y guardar la firma; la firma queda almacenada en el perfil y disponible para futuras firmas de documentos.

---

### CA-011: Estado del contrato SAD (pendiente) ← HU-025

> [INCOMPLETO] — Pendiente de gap [P-006]: qué tipo(s) de contrato se muestran en "Estado del contrato" (dimensión jurídica, de jornada, o ambas) no está definido.

---

### CA-012: Estado del contrato SAD — datos disponibles ← HU-025
GIVEN la trabajadora SAD accede a "Estado del contrato"
WHEN la pantalla se carga
THEN se muestran la fecha de inicio del contrato y el número de empleada; hay un enlace para descargar el PDF del contrato actual; la información es de solo lectura.

---

## Checklist de Validación
- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de éxito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [x] Ambigüedades resueltas (las resolubles; las pendientes marcadas como [INCOMPLETO])
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes
- [ ] Tipo de contrato alineado con backend ([P-006])

---

## Fuera de Alcance
- Gestión activa de pagos/nóminas (el acceso de solo lectura a documentos de nómina está dentro del alcance como parte de Documentación laboral)
