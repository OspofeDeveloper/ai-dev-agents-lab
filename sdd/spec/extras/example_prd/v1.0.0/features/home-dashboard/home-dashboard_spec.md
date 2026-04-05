# Spec: Home Dashboard
> Versión: 1.0 | Fecha: 2026-04-02
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-002

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades. Usa la app CUIDEO (identidad visual azul). | Ver home con accesos rápidos, indicador de completitud de perfil, badges de pendientes, comunicados y mensajes del sistema. |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Ver home con servicio activo, próximos servicios, llamamientos pendientes, avisos, badges de documentación y comunicados del sistema. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Publicar comunicados en el tablón, enviar mensajes del sistema, fijar contenidos importantes. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-006: Navegar por el panel principal (perfil SAD)
Como trabajadora SAD / quiero ver un panel principal que me muestre mi situación actual (servicio activo, próximos servicios, llamamientos pendientes, avisos) / para que pueda gestionar mi jornada de un vistazo.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-002]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-007: Navegar por el panel principal (perfil Hogar)
Como trabajadora Hogar / quiero ver un panel principal con accesos rápidos a ofertas, disponibilidad, perfil y comunicación / para que pueda acceder a las secciones principales con el mínimo de pasos.

### HU-008: Leer comunicados del tablón de anuncios
Como trabajadora (Hogar o SAD) / quiero consultar los comunicados publicados por la empresa / para que esté informada de novedades, protocolos y formaciones relevantes.

### HU-009: Ver mensajes del sistema
Como trabajadora (Hogar o SAD) / quiero ver los mensajes administrativos que me envía el sistema / para que pueda leer avisos importantes y mantener el buzón organizado.

---

## Recorridos de Usuario

### Journey 1: Acceder a la home por primera vez tras login
Actor: Trabajadora Hogar o SAD | Objetivo: Ver la pantalla principal tras completar el onboarding

1. La trabajadora abre la app por primera vez.
2. La app muestra la pantalla de splash con el logo de la marca durante 2-3 segundos.
3. No hay sesión activa; la app redirige al login.
4. La trabajadora inicia sesión (Hogar: con email y contraseña; SAD: con email y contraseña).
5. Tras el login exitoso, la app solicita permiso de notificaciones push.
6. La app muestra las pantallas de onboarding (3-5 pantallas con los highlights principales).
7. La app solicita permiso de ubicación con explicación del uso para fichaje.
8. El onboarding finaliza y la trabajadora llega a la pantalla principal (home).

Estado de éxito: La trabajadora ve su home personalizada (Hogar o SAD) y la app no vuelve a mostrar el onboarding en aperturas posteriores.

Flujos alternativos:
- Si ya hay una sesión válida al abrir la app → salta directamente a la home, sin mostrar login ni onboarding.
- Si el token de sesión ha expirado → muestra el login; tras iniciar sesión, ya no muestra onboarding (solo se muestra una vez).

---

## Resultados y Éxito

- **Comunicación efectiva**: Los mensajes enviados a coordinación se entregan y la trabajadora recibe respuesta en la misma conversación. Los mensajes nuevos llegan en tiempo real.
- **Documentación gestionada**: Los documentos subidos quedan disponibles en su categoría. Los documentos laborales pendientes de firma muestran badge de alerta.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Perfiles diferenciados:**
- El producto se presenta como dos aplicaciones de marca diferenciada (CUIDEO para perfil Hogar con identidad visual azul, Felizvita para perfil SAD con identidad visual verde) que comparten las mismas funcionalidades de base y adaptan su contenido al tipo de contrato de la trabajadora.
- Los colores exactos de marca serán provistos por el cliente en las guías de marca.
- Las funcionalidades exclusivas de cada perfil están indicadas en las HUs y CAs correspondientes.

**Comunicación:**
- Los mensajes del chat se actualizan en tiempo real sin necesidad de recargar la pantalla.
- Las notificaciones push se entregan incluso cuando la app está en segundo plano o cerrada.

**Mensajes del sistema:**
- Los mensajes del sistema se presentan en dos niveles de criticidad: alta (se muestran primero y de forma diferenciada) y normal.
- Los mensajes del sistema no se pueden responder.

**Completitud del perfil (Hogar):**
- [P-013 — asunción aplicada]: El porcentaje de completitud computa los campos de Información Personal, Profesional e Idiomas. La foto de perfil suma al porcentaje pero es opcional. El indicador visible en home solo aplica al perfil Hogar.

**Documentos:**
- Los documentos pendientes de firma generan badge/aviso en la sección de Documentos y en la home.

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Home SAD | Toca CTA de llamamiento pendiente | Detalle del llamamiento |
| Notificación push | Toca notificación | Pantalla específica relacionada via deeplink |
| Historial de notificaciones | Toca una notificación | Contenido relacionado via deeplink |

---

## Criterios de Aceptación

### CA-001: Home Hogar — accesos directos ← HU-007
GIVEN la trabajadora Hogar está en la home
WHEN la home se carga
THEN se muestran accesos directos a: Ofertas, Mi Disponibilidad, Perfil, Comunicación.

---

### CA-002: Home Hogar — porcentaje de completitud visible ← HU-007
GIVEN la trabajadora Hogar está en la home
WHEN la home se carga
THEN se muestra el indicador de porcentaje de completitud del perfil de forma visible para incentivar su cumplimentación.

---

### CA-003: Home SAD — servicio activo + siguiente ← HU-006
GIVEN la trabajadora SAD está en la home
WHEN la home se carga
THEN el bloque de servicios muestra como máximo el servicio activo y el siguiente servicio; si hay más, muestra el enlace "Ver más servicios".

---

### CA-004: Home SAD — llamamiento pendiente muy visible ← HU-006
GIVEN la trabajadora SAD tiene un llamamiento pendiente de respuesta
WHEN abre la home
THEN el llamamiento se muestra de forma muy visible con indicación de urgencia y cuenta atrás de caducidad; el CTA lleva al detalle del llamamiento (no permite aceptar/rechazar directamente desde la home).

---

### CA-005: Home SAD — estados de la home (pendiente) ← HU-006

> [INCOMPLETO] — Pendiente de gap [P-002]: los estados posibles de la home SAD y qué muestra la home en cada estado (sin servicios, con servicio activo, con próximo servicio, con llamamiento pendiente, con ambos simultáneamente, etc.) no están definidos. CAs de cada estado no pueden completarse hasta resolver el gap.

---

### CA-006: Home SAD — documentación pendiente de firma ← HU-006
GIVEN la trabajadora SAD tiene documentación pendiente de firma
WHEN abre la home
THEN se muestra un badge/contador destacado para documentación pendiente de firma como elemento de alta prioridad.

---

### CA-007: Home SAD — bloque "Últimos avisos" ← HU-006
GIVEN la trabajadora SAD está en la home
WHEN la home se carga
THEN se muestra el bloque "Últimos avisos" con 2-3 items y acceso al listado completo.

---

### CA-008: Home — nombre y foto en cabecera ← HU-007 / HU-006
GIVEN la trabajadora (Hogar o SAD) está en la home
WHEN la home se carga
THEN se muestra el nombre de la trabajadora y su foto de perfil (o placeholder si no tiene foto) en la cabecera.

---

### CA-009: Home — pull-to-refresh ← HU-007 / HU-006
GIVEN la trabajadora (Hogar o SAD) está en la home
WHEN realiza un gesto de pull-to-refresh
THEN la home actualiza los datos mostrados.

---

### CA-010: Home — badges en accesos directos ← HU-007 / HU-006
GIVEN hay mensajes no leídos o acciones pendientes
WHEN la trabajadora ve la home
THEN los accesos directos correspondientes muestran un badge o contador.

---

### CA-011: Tablón — listado de comunicados diferenciado ← HU-008
GIVEN la trabajadora accede al tablón de anuncios
WHEN la lista se carga
THEN se muestran comunicados diferenciando entre contenidos fijos (protocolo, calendario laboral, PRL, documentos de referencia permanente) y comunicaciones variables (recordatorios, campañas, novedades); el backoffice puede fijar contenidos importantes en la parte superior.

---

### CA-012: Tablón — detalle y marcar como leído ← HU-008
GIVEN la trabajadora toca un comunicado en la lista
WHEN abre el detalle
THEN se muestra el título, fecha, texto completo, imágenes y adjuntos si los hay; el comunicado queda marcado como leído automáticamente.

---

### CA-013: Tablón — indicador de no leído ← HU-008
GIVEN hay comunicados no leídos
WHEN la trabajadora ve el tablón o el menú/tab correspondiente
THEN se muestra un badge indicando contenido nuevo no leído.

---

### CA-014: Mensajes del sistema — lista con criticidad ← HU-009
GIVEN la trabajadora accede a los mensajes del sistema
WHEN la lista se carga
THEN los mensajes de criticidad alta se muestran primero y de forma diferenciada; los de criticidad normal aparecen debajo.

---

### CA-015: Mensajes del sistema — borrar y marcar como leído ← HU-009
GIVEN la trabajadora está en los mensajes del sistema
WHEN toca un mensaje
THEN se muestra el contenido completo con adjuntos si los hay; el mensaje queda marcado como leído automáticamente; la trabajadora tiene opción de borrar el mensaje.

---

### CA-016: Mensajes del sistema — sin opción de respuesta ← HU-009
GIVEN la trabajadora está en el detalle de un mensaje del sistema
WHEN ve las opciones disponibles
THEN no existe botón de redactar respuesta; los mensajes son de solo lectura.

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
- [ ] Estados de home SAD definidos con cliente ([P-002])

---

## Fuera de Alcance
- Autenticación biométrica (Face ID, huella digital)
- Autenticación de dos factores (2FA)
- Configuración de preferencias de notificaciones por tipo (previsto para una fase futura)
