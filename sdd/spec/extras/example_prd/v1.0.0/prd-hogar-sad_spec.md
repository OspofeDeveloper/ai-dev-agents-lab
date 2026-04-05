# Spec: Aplicaciones Móviles CUIDEO - Hogar & SAD
> Versión: 1.0 | Fecha: 2026-04-02 | Generado desde: prd-hogar-sad.md

---

## Resumen de generación

### Estado de los 8 elementos SDD

| Elemento | Estado |
|----------|--------|
| Actores | COMPLETO — 3 actores definidos con capacidades diferenciadas por perfil |
| Historias de Usuario | INCOMPLETO — 8 HUs marcadas [INCOMPLETO] por gaps críticos sin responder (P-001 a P-008) |
| Recorridos de Usuario | INCOMPLETO — journeys de login con bloqueo (P-001), home SAD (P-002) y llamamientos (P-004/P-008) parciales por gaps críticos |
| Resultados y Éxito | COMPLETO — estados de éxito definidos para todos los flujos con información disponible |
| Instrucciones Inambiguas | INCOMPLETO — reglas de tipo contrato (P-006), datos de salud (P-003) y cómputo de vacaciones (P-005) pendientes |
| Criterios de Aceptación | INCOMPLETO — CAs de HUs afectadas por gaps críticos generados parcialmente o omitidos con referencia al gap |
| Checklist de Validación | COMPLETO — items verificables desde el spec marcados; items que requieren validación humana sin marcar |
| Fuera de Alcance | COMPLETO — exclusiones funcionales listadas (contaminaciones técnicas eliminadas per C-012) |

### HUs incompletas

| HU | Título | Gaps pendientes |
|----|--------|-----------------|
| HU-003 | Iniciar sesión en la app | [P-001] |
| HU-006 | Navegar por el panel principal (perfil SAD) | [P-002] |
| HU-010 | Ver detalle de un servicio (SAD) | [P-003] |
| HU-012 | Responder a un llamamiento | [P-004], [P-008] |
| HU-019 | Consultar historial de ausencias y saldo de vacaciones | [P-005] |
| HU-022 | Ver y editar mi perfil | [P-006] |
| HU-025 | Ver el estado de mi contrato (SAD) | [P-006] |
| HU-004 | Activar mi cuenta (SAD) | [P-007] |

### Asunciones por defecto aplicadas

| Sección | Asunción aplicada | Origen (gap) |
|---------|-------------------|--------------|
| HU-031 Historial de notificaciones | La app muestra un listado de notificaciones recibidas con título, cuerpo y fecha; tocar una notificación abre el contenido relacionado mediante deeplink; existe la opción de marcar todas como leídas. No se puede borrar notificaciones individuales desde el historial. | [P-009] |
| HU-030 Notificaciones push — tipos | Se envía una notificación separada por servicio programado para el día siguiente, cada una con deeplink al detalle del servicio correspondiente. | [P-010] |
| HU-015 Navegar ofertas — estado vacío | Se muestra un mensaje genérico "No se han encontrado ofertas con los filtros actuales" con un botón para limpiar filtros. No se diferencia entre filtros activos o ausencia total de ofertas. | [P-011] |
| HU-027 Borrar conversación con mensajes no leídos | La trabajadora puede borrar cualquier conversación con confirmación, independientemente del estado de lectura. El diálogo de confirmación estándar no hace referencia a mensajes no leídos. | [P-012] |
| HU-022 Completitud del perfil — campos que computan | El porcentaje de completitud computa los campos de la sección Información Personal, Profesional e Idiomas. La foto de perfil suma al porcentaje pero es opcional. El cálculo exacto lo provee el backend. El indicador visible en home solo aplica al perfil Hogar. | [P-013] |

### Contaminaciones de Pureza procesadas

| ID | Acción | Detalle |
|----|--------|---------|
| C-001 | ACEPTAR | Stack KMM reescrito como descripción funcional de doble marca |
| C-002 | ACEPTAR | JWT/Sanctum reescrito como comportamiento de sesión de 30 días |
| C-003 | ACEPTAR | iOS Keychain / Android Keystore reescrito como almacenamiento seguro del dispositivo |
| C-004 | ACEPTAR | Firebase reescrito como capacidades funcionales (tiempo real, push, background) |
| C-005 | ACEPTAR | Endpoints de API eliminados del Spec |
| C-006 | ACEPTAR | Módulos KMM eliminados del Spec |
| C-007 | ACEPTAR | Bundle IDs, colores hex y versiones OS reescritos funcionalmente |
| C-008 | ACEPTAR | Compresión/tamaño reescritos como comportamiento observable para el usuario |
| C-009 | ACEPTAR | TLS/certificate pinning reescrito como comunicación cifrada |
| C-010 | ACEPTAR | Métricas de ms reescritas como confirmación visual inmediata e indicador de progreso |
| C-011 | ACEPTAR | "Arquitectura admite múltiples idiomas" reescrito como capacidad funcional de la app |
| C-012 | ACEPTAR | Exclusiones técnicas de Fuera de Alcance eliminadas |

---

## Actores

| Actor | Descripción | Capacidades en este spec |
|-------|-------------|--------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades. Usa la app CUIDEO (identidad visual azul). | Registro y login, navegar y solicitar ofertas, gestionar disponibilidad semanal, gestionar perfil y documentos, comunicarse con coordinación, recibir notificaciones. |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Login y activación de cuenta, gestionar servicios asignados, fichar entrada/salida con geolocalización, responder llamamientos con firma digital, reportar incidencias, solicitar ausencias, gestionar disponibilidad semanal, gestionar perfil y documentos, comunicarse con coordinación, recibir notificaciones. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Crear cuentas SAD, enviar llamamientos, aprobar ausencias, gestionar comunicados, configurar parámetros del sistema, cerrar conversaciones. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-001: Ver la pantalla de splash al abrir la app
Como trabajadora (Hogar o SAD) / quiero ver una pantalla de bienvenida con el logo de la app al abrirla / para que la app se identifique visualmente antes de redirigirme al flujo de acceso.

### HU-002: Completar el onboarding inicial
Como trabajadora (Hogar o SAD) / quiero ver un onboarding con las funcionalidades principales de la app la primera vez que accedo / para que pueda entender qué puedo hacer con la app antes de usarla.

### HU-003: Iniciar sesión en la app
Como trabajadora (Hogar o SAD) / quiero iniciar sesión con mi email y contraseña / para que pueda acceder a la app de forma segura y mantener mi sesión activa sin necesidad de volver a hacer login en cada acceso.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-004: Activar mi cuenta (SAD)
Como trabajadora SAD / quiero activar mi cuenta desde el enlace que recibo por email / para que pueda establecer mis credenciales y acceder a la app por primera vez.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-007]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-005: Registrarme en la app (Hogar)
Como trabajadora Hogar / quiero registrarme en la app introduciendo mi email y contraseña / para que pueda crear mi cuenta y empezar a usar la app.

### HU-006: Navegar por el panel principal (perfil SAD)
Como trabajadora SAD / quiero ver un panel principal que me muestre mi situación actual (servicio activo, próximos servicios, llamamientos pendientes, avisos) / para que pueda gestionar mi jornada de un vistazo.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-002]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-007: Navegar por el panel principal (perfil Hogar)
Como trabajadora Hogar / quiero ver un panel principal con accesos rápidos a ofertas, disponibilidad, perfil y comunicación / para que pueda acceder a las secciones principales con el mínimo de pasos.

### HU-008: Leer comunicados del tablón de anuncios
Como trabajadora (Hogar o SAD) / quiero consultar los comunicados publicados por la empresa / para que esté informada de novedades, protocolos y formaciones relevantes.

### HU-009: Ver mensajes del sistema
Como trabajadora (Hogar o SAD) / quiero ver los mensajes administrativos que me envía el sistema / para que pueda leer avisos importantes y mantener el buzón organizado.

### HU-010: Ver el detalle de un servicio (SAD)
Como trabajadora SAD / quiero ver toda la información de un servicio asignado (datos del cliente, ubicación, plan de cuidados, tareas, documentos) / para que pueda prepararme y ejecutar el servicio correctamente.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-003]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-011: Consultar mis servicios asignados (SAD)
Como trabajadora SAD / quiero ver el listado de todos mis servicios agrupados por estado / para que pueda saber qué servicios tengo activos, próximos y completados.

### HU-012: Responder a un llamamiento (SAD)
Como trabajadora SAD / quiero aceptar o rechazar un llamamiento con mi firma digital / para que quede constancia legal de mi decisión sobre el turno ofrecido.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-004], [P-008]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-013: Gestionar notas de un servicio (SAD)
Como trabajadora SAD / quiero añadir, editar y borrar notas sobre la evolución del servicio / para que las coordinadoras estén informadas de lo que ocurre en el servicio en tiempo real.

### HU-014: Recibir y confirmar un nuevo servicio asignado (SAD — contrato indefinido)
Como trabajadora SAD con contrato indefinido / quiero recibir una notificación cuando me asignan un nuevo servicio y confirmar que lo he visto / para que quede registrado que he recibido la información.

### HU-015: Navegar y filtrar ofertas de trabajo (Hogar)
Como trabajadora Hogar / quiero consultar las ofertas disponibles con filtros de zona, horario y fecha / para que pueda encontrar oportunidades de trabajo que se ajusten a mis preferencias.

### HU-016: Solicitar una oferta de trabajo (Hogar)
Como trabajadora Hogar / quiero enviar mi solicitud a una oferta con un solo toque / para que coordinación pueda revisar mi candidatura.

### HU-017: Consultar mis solicitudes de oferta (Hogar)
Como trabajadora Hogar / quiero ver el estado de todas mis solicitudes enviadas / para que pueda hacer seguimiento de mis candidaturas y retirar las que ya no me interesan.

### HU-018: Fichar entrada y salida en un servicio (SAD)
Como trabajadora SAD / quiero fichar mi entrada y salida en un servicio con geolocalización / para que quede registro verificado del tiempo que he trabajado.

### HU-019: Consultar historial de ausencias y saldo de vacaciones (SAD)
Como trabajadora SAD / quiero ver todas mis solicitudes de ausencia con su estado y los contadores de vacaciones disponibles / para que pueda planificar mis ausencias conociendo mi saldo real.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-005]. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

### HU-020: Solicitar una ausencia (SAD)
Como trabajadora SAD / quiero solicitar vacaciones, baja médica u otro tipo de ausencia / para que coordinación pueda revisarla y aprobarla.

### HU-021: Reportar una incidencia (SAD)
Como trabajadora SAD / quiero reportar una incidencia del servicio o del cliente con descripción y adjuntos / para que coordinación sea informada de inmediato.

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

### HU-026: Gestionar mi disponibilidad semanal
Como trabajadora (Hogar o SAD) / quiero declarar mis franjas de disponibilidad y no disponibilidad en el calendario semanal / para que el sistema pueda asignarme servicios en los horarios en que estoy disponible.

### HU-027: Comunicarme con coordinación mediante chat
Como trabajadora (Hogar o SAD) / quiero iniciar conversaciones y enviar mensajes al equipo de coordinación / para que pueda resolver dudas, gestionar incidencias o tratar temas laborales de forma ágil.

### HU-028: Ver mi historial de conversaciones
Como trabajadora (Hogar o SAD) / quiero ver todas mis conversaciones con coordinación, incluyendo las cerradas / para que pueda consultar el historial de comunicaciones previas.

### HU-029: Cerrar sesión
Como trabajadora (Hogar o SAD) / quiero cerrar sesión de forma explícita / para que mis datos queden protegidos si comparto o pierdo el dispositivo.

### HU-030: Recibir notificaciones push
Como trabajadora (Hogar o SAD) / quiero recibir notificaciones push para eventos relevantes (mensajes, llamamientos, cambios de estado, recordatorios) / para que pueda reaccionar a tiempo sin necesidad de abrir la app constantemente.

### HU-031: Consultar el historial de notificaciones
Como trabajadora (Hogar o SAD) / quiero ver un historial de las notificaciones recibidas / para que pueda revisar avisos que no leí en el momento.

### HU-032: Ver pantalla de acceso revocado (SAD)
Como trabajadora SAD cuya cuenta ha sido suspendida o dada de baja / quiero ver una pantalla informativa en lugar de acceder a la app / para que entienda que ya no tengo acceso y sepa a dónde dirigirme.

### HU-033: Consultar historial de fichajes (SAD)
Como trabajadora SAD / quiero ver el registro de mis entradas y salidas agrupado por servicio y día / para que pueda revisar las horas registradas en cada servicio.

### HU-034: Consultar historial de incidencias (SAD)
Como trabajadora SAD / quiero ver todas las incidencias que he reportado con su estado y los comentarios de coordinación / para que pueda hacer seguimiento de su resolución.

### HU-035: Recuperar el acceso a mi cuenta
Como trabajadora (Hogar o SAD) / quiero recuperar el acceso a mi cuenta si olvido mi contraseña / para que pueda volver a usar la app sin necesidad de contactar con soporte.

---

## Recorridos de Usuario

### Journey 1: Primera apertura y onboarding
Actor: Trabajadora Hogar o SAD | Objetivo: Llegar a la pantalla principal tras instalar la app

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

### Journey 2: Login con sesión persistente
Actor: Trabajadora Hogar o SAD | Objetivo: Acceder a la app sin volver a hacer login

1. La trabajadora abre la app (no es la primera vez).
2. La app verifica la validez de la sesión almacenada.
3. La sesión es válida; la app redirige directamente a la home.

Estado de éxito: La trabajadora llega a la home sin ver la pantalla de login.

Flujos alternativos:
- Si la sesión ha expirado (más de 30 días sin uso) → muestra el login.
- Si el token ha sido revocado por el backend (cuenta suspendida/baja) → muestra la pantalla de acceso revocado (SAD) o pantalla de login con error (Hogar).
- Si múltiples operaciones en curso reciben respuesta de sesión inválida simultáneamente → se muestra el login una única vez, se cancelan las operaciones pendientes, no aparecen múltiples diálogos de error superpuestos.

---

### Journey 3: Activación de cuenta por primera vez (SAD)
Actor: Trabajadora SAD | Objetivo: Establecer credenciales y acceder a la app

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-007]. El flujo exacto (qué pantalla abre el enlace, qué introduce la trabajadora, destino tras completar) no está definido. Responde en el _analysis.md y ejecuta /wf-spec-delta para completar.

1. La trabajadora recibe un email de activación enviado desde el backoffice.
2. La trabajadora pulsa el enlace del email.
3. [PENDIENTE P-007: flujo de activación — pantalla, campos y destino no definidos]

---

### Journey 4: Fichar entrada y salida en un servicio (SAD)
Actor: Trabajadora SAD | Objetivo: Registrar inicio y fin de un servicio con geolocalización

1. La trabajadora abre la app cuando está próxima la hora del servicio.
2. El botón de fichaje está habilitado (se activa 30 minutos antes del inicio del servicio).
3. La trabajadora accede al fichaje desde la home, el tab de fichaje o el detalle del servicio.
4. La trabajadora selecciona el servicio de la lista de servicios activos.
5. La trabajadora pulsa "Fichar entrada".
6. La app captura las coordenadas GPS. Si la precisión es baja, muestra una advertencia; espera máximo 2 segundos y permite continuar igualmente.
7. El fichaje se registra. La app muestra un contador de tiempo transcurrido y el botón "Fichar salida".
8. Al finalizar el servicio, la trabajadora pulsa "Fichar salida".
9. La app muestra un diálogo de confirmación.
10. Al confirmar, se registra la salida.

Estado de éxito: Ambos fichajes quedan registrados con coordenadas y hora. La trabajadora ve el tiempo trabajado en el historial de ese servicio.

Flujos alternativos:
- Si el botón está aún deshabilitado → muestra "Disponible en X min" con indicación visual del tiempo restante.
- Si la trabajadora no ficha la salida tras finalizar el servicio → la app muestra un aviso visible (banner o notificación in-app) recordando la acción pendiente; este aviso no bloquea la navegación.
- Si la trabajadora no puede fichar (no asistencia) → puede reportar una incidencia de fichaje directamente desde la pantalla de fichaje.
- La trabajadora también puede solicitar una ausencia desde la pantalla de fichaje.

---

### Journey 5: Responder a un llamamiento (SAD)
Actor: Trabajadora SAD | Objetivo: Aceptar o rechazar un turno ofrecido con firma digital

1. La trabajadora recibe una notificación push de nuevo llamamiento.
2. La trabajadora abre la notificación y llega al detalle del llamamiento en la app, o accede desde la home donde el llamamiento se muestra de forma muy visible con cuenta atrás.
3. Desde la home, la trabajadora pulsa el CTA que lleva al detalle del llamamiento (no puede aceptar/rechazar directamente desde la home).
4. La trabajadora está en el detalle del llamamiento. La navegación hacia atrás queda bloqueada hasta que tome una decisión.
5. La trabajadora ve la información completa del llamamiento: código de servicio, fecha/hora, ubicación, urgencia y cuenta atrás de caducidad.
6a. Si la trabajadora acepta: se muestra un diálogo con el texto de aceptación. La trabajadora firma digitalmente con el dedo y confirma.
6b. Si la trabajadora rechaza: se muestra un diálogo para seleccionar el motivo (No disponible, Demasiado lejos, Motivos personales, Otros — con campo de texto). La trabajadora firma digitalmente con el dedo y confirma.
7. El llamamiento queda registrado como aceptado o rechazado.

Estado de éxito: La firma digital queda registrada. El llamamiento aparece en el historial con su resultado. Si fue aceptado, el servicio aparece en la lista de servicios de la trabajadora.

Flujos alternativos:
- Si el llamamiento caduca mientras la trabajadora está en el detalle → [PENDIENTE P-004: comportamiento al caducar sin respuesta].
- Si otro compañero acepta primero el llamamiento → el llamamiento aparece como desactivado/no disponible en la lista.
- Los textos legales de los diálogos de firma → [PENDIENTE P-008].

---

### Journey 6: Solicitar una ausencia (SAD)
Actor: Trabajadora SAD | Objetivo: Enviar una solicitud de ausencia para aprobación

1. La trabajadora accede a "Solicitar Ausencia" desde la home o el menú.
2. Selecciona el tipo de ausencia (Vacaciones, Permiso personal, Baja médica, Baja voluntaria, Asuntos propios, Otros).
3. Selecciona el rango de fechas (inicio y fin, con opción de medio día en ambas).
4. La app muestra el saldo de vacaciones disponible (si aplica al tipo seleccionado).
5. Si las fechas entran en conflicto con servicios asignados, la app muestra una advertencia.
6. La trabajadora introduce el motivo/descripción (obligatorio en los tipos que lo requieren).
7. Si es baja médica de más de 3 días, adjunta el certificado médico (obligatorio).
8. La trabajadora envía la solicitud.
9. La app confirma el envío y la trabajadora recibe una notificación push de confirmación.

Estado de éxito: La solicitud aparece en el historial de ausencias con estado "Pendiente" y la trabajadora recibe notificación de cambio de estado cuando coordinación la resuelve.

Flujos alternativos:
- Si la trabajadora quiere cancelar una solicitud pendiente → puede hacerlo desde el historial de ausencias.

---

### Journey 7: Solicitar una oferta de trabajo (Hogar)
Actor: Trabajadora Hogar | Objetivo: Enviar candidatura a una oferta que le interesa

1. La trabajadora accede al listado de ofertas desde la home.
2. Navega por las ofertas (puede filtrar por zona, horario, rango de fechas; ordenar por recientes, más cercanas o tarifa más alta).
3. La trabajadora toca una oferta para ver los detalles completos.
4. Pulsa el botón "Aplicar".
5. La app muestra un diálogo de confirmación con el resumen de la oferta.
6. La trabajadora confirma con un toque.
7. La solicitud se envía. La app muestra un mensaje de éxito y la trabajadora recibe notificación de confirmación.

Estado de éxito: La solicitud aparece en "Mis solicitudes" con estado "Pendiente". La trabajadora recibe notificación push cuando el estado cambia.

Flujos alternativos:
- Si el perfil de la trabajadora está incompleto al intentar aplicar → la app muestra una advertencia con los campos obligatorios pendientes y acceso directo para completarlos.
- Si la trabajadora ya ha enviado una solicitud a esa oferta → la app impide enviar un duplicado.
- Si no hay ofertas que coincidan con los filtros → se muestra el mensaje "No se han encontrado ofertas con los filtros actuales" con un botón para limpiar filtros (asunción P-011).

---

### Journey 8: Iniciar una conversación con coordinación
Actor: Trabajadora Hogar o SAD | Objetivo: Contactar con coordinación para tratar un tema laboral

1. La trabajadora accede al módulo de Comunicación.
2. Pulsa el botón de nueva conversación.
3. La app muestra una selección de asuntos predefinidos: Vacaciones/Ausencia, Nómina/Facturación, Sobre un servicio, Documentación, Consulta general, Otros.
4. La trabajadora selecciona el asunto.
5. Opcionalmente, enlaza contexto (selecciona servicio u oferta relacionados).
6. La trabajadora escribe su primer mensaje (obligatorio).
7. La conversación se crea y la trabajadora ve el hilo de chat. La cabecera muestra el asunto seleccionado (y el código de ticket si el backend lo provee).
8. La trabajadora ve la conversación como si fuera con "Coordinación", independientemente del enrutado interno.

Estado de éxito: La conversación aparece en el listado con el último mensaje visible. La trabajadora puede continuar enviando mensajes. Los mensajes se actualizan en tiempo real sin necesidad de recargar.

Flujos alternativos:
- Si la conversación ha sido cerrada por coordinación → la trabajadora puede leer el historial pero no puede enviar nuevos mensajes; se muestra el aviso "Conversación cerrada".

---

## Resultados y Éxito

- **Autenticación completada**: La trabajadora llega a su home personalizada sin ver pantallas de login en aperturas posteriores hasta que la sesión expire (30 días de inactividad) o cierre sesión explícitamente.
- **Servicio gestionado correctamente**: La trabajadora SAD ha fichado entrada y salida con geolocalización; los registros aparecen en el historial con hora, fecha y duración. Las coordinadoras pueden ver las notas registradas sobre el servicio.
- **Llamamiento respondido**: La firma digital de la trabajadora queda almacenada junto a la decisión (aceptación o rechazo) y el llamamiento aparece en el historial con su resultado y fecha.
- **Ausencia solicitada**: La solicitud aparece en el historial con estado "Pendiente"; los contadores de vacaciones reflejan los días pendientes de aprobación.
- **Oferta solicitada (Hogar)**: La candidatura aparece en "Mis solicitudes" con estado "Pendiente"; la trabajadora recibe notificación push en cada cambio de estado.
- **Comunicación efectiva**: Los mensajes enviados a coordinación se entregan y la trabajadora recibe respuesta en la misma conversación. Los mensajes nuevos llegan en tiempo real.
- **Perfil actualizado**: Los cambios guardados se reflejan inmediatamente en la app. El porcentaje de completitud aumenta al añadir información (perfil Hogar).
- **Documentación gestionada**: Los documentos subidos quedan disponibles en su categoría. Los documentos laborales pendientes de firma muestran badge de alerta.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Sesión y autenticación:**
- La sesión se mantiene activa durante 30 días desde el último uso. Expira si la trabajadora lleva 30 días sin acceder, cierra sesión explícitamente, o su cuenta es revocada por administración.
- Las credenciales de sesión se almacenan en el área de seguridad del dispositivo, protegidas contra acceso no autorizado por otras aplicaciones.
- Toda la comunicación de la app con el servidor está cifrada y protegida contra interceptación.
- Al detectar sesión inválida durante múltiples operaciones simultáneas: mostrar el login una única vez, cancelar las operaciones pendientes, no mostrar múltiples diálogos de error.

**Perfiles diferenciados:**
- El producto se presenta como dos aplicaciones de marca diferenciada (CUIDEO para perfil Hogar con identidad visual azul, Felizvita para perfil SAD con identidad visual verde) que comparten las mismas funcionalidades de base y adaptan su contenido al tipo de contrato de la trabajadora.
- Los colores exactos de marca serán provistos por el cliente en las guías de marca.
- Las funcionalidades exclusivas de cada perfil están indicadas en las HUs y CAs correspondientes.

**Control horario (SAD):**
- El botón de fichaje de entrada se activa 30 minutos antes del inicio del servicio; fuera de esa ventana aparece deshabilitado con indicación visual del tiempo restante.
- El botón de fichaje muestra estados dinámicos según la hora: "Disponible en X min", "Fichar entrada", "Fichada · en servicio", "Fichar salida", "Servicio finalizado".
- No se permite fichaje manual desde la app; las correcciones de fichaje se gestionan desde backoffice.
- Si la trabajadora no ficha la salida tras finalizar el servicio, se muestra un aviso visible (banner o notificación in-app) que recuerda la acción pendiente. Este aviso no bloquea la navegación.
- Múltiples servicios en el mismo día se fichan de forma independiente; no se bloquean entre sí.

**Llamamientos (SAD):**
- La aceptación y el rechazo de llamamientos solo son posibles desde el detalle del llamamiento, nunca directamente desde la home.
- Una vez dentro del detalle del llamamiento, la navegación hacia atrás queda bloqueada hasta que la trabajadora acepte o rechace.
- Tanto la aceptación como el rechazo requieren firma digital de la trabajadora.
- Los motivos de rechazo disponibles son: No disponible, Demasiado lejos, Motivos personales, Otros (con campo de texto libre).
- Cuando un llamamiento caduca o es aceptado por otra trabajadora, se muestra como desactivado/no disponible en la lista.
- [PENDIENTE P-004]: comportamiento exacto cuando un llamamiento caduca sin respuesta (¿estado "sin respuesta" o "rechazo por inacción"? ¿notificación a la trabajadora?).

**Disponibilidad:**
- Los cambios en franjas de disponibilidad se guardan de forma inmediata al confirmar cada slot (no hay botón "guardar todo").
- Los slots de tipo "Activa" (horas con servicio asignado por planificación) son de solo lectura; no se pueden editar ni eliminar desde la app.
- Se permiten solapamientos entre slots de distinto tipo (Disponible + No disponible); no se permiten solapamientos entre slots del mismo tipo.
- Las reglas de negocio de disponibilidad (máx. 8h/día, mínimo 12h de descanso entre jornadas) las valida y gestiona exclusivamente el servidor; la app muestra el error si la API lo devuelve.

**Documentos:**
- Documentación personal (DNI/NIE, certificados, etc.): la trabajadora puede subir y reemplazar pero no eliminar.
- Documentación laboral (contrato, nóminas, etc.): la trabajadora puede consultar, descargar y firmar; no puede subir ni eliminar.
- Los documentos pendientes de firma generan badge/aviso en la sección de Documentos y en la home.

**Perfil:**
- Los datos core del perfil (nombre, apellidos, DNI/NIE) son de solo lectura.
- La dirección de domicilio es editable.
- Para el DNI/NIE: se muestra la fecha de vencimiento y existe un flujo para "proponer nueva fecha + adjuntar documento" que el backoffice valida; la trabajadora no edita el dato existente directamente.
- [PENDIENTE P-006]: qué tipo(s) de contrato se muestran en el perfil SAD y en "Estado del contrato" (dimensión jurídica: Indefinido/Fijo Discontinuo; dimensión de jornada: Tiempo completo/Tiempo parcial; o ambas).

**Completitud del perfil (Hogar):**
- Al intentar aplicar a una oferta con perfil incompleto, se muestra una advertencia o bloqueo informando de los campos obligatorios pendientes, con acceso directo a completarlos.
- [P-013 — asunción aplicada]: El porcentaje de completitud computa los campos de Información Personal, Profesional e Idiomas. La foto de perfil suma al porcentaje pero es opcional. El indicador visible en home solo aplica al perfil Hogar.

**Comunicación:**
- Los mensajes del chat se actualizan en tiempo real sin necesidad de recargar la pantalla.
- Las notificaciones push se entregan incluso cuando la app está en segundo plano o cerrada.
- Al crear una conversación, la trabajadora siempre ve el chat como una conversación con "Coordinación", independientemente del enrutado interno del backoffice.

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.
- La app puede mostrarse en múltiples idiomas. El lanzamiento inicial es en castellano; la estructura permite añadir catalán, inglés y francés en versiones futuras.
- La trabajadora puede adjuntar fotos y documentos. El sistema informa si un archivo no puede enviarse antes de intentar la subida.

**Mensajes del sistema:**
- Los mensajes del sistema se presentan en dos niveles de criticidad: alta (se muestran primero y de forma diferenciada) y normal.
- Los mensajes del sistema no se pueden responder.

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Splash | Hay sesión válida al abrir | Home (según perfil) |
| Splash | No hay sesión válida | Login |
| Login | Login exitoso | Solicitud permiso notificaciones push → Onboarding (solo primera vez) → Home |
| Login | Login exitoso (no primera vez) | Home (según perfil) |
| Login | Cuenta suspendida / revocada (SAD) | Pantalla de acceso revocado |
| Home SAD | Toca CTA de llamamiento pendiente | Detalle del llamamiento |
| Detalle del llamamiento | Decisión tomada (acepta o rechaza) | Desbloqueo de navegación → Home u otra sección |
| Home SAD / Tab fichaje / Detalle servicio | Pulsa fichar entrada | Selección de servicio activo → Confirmación de fichaje |
| Oferta (detalle) | Pulsa "Aplicar" (perfil completo) | Diálogo de confirmación → Mensaje de éxito |
| Oferta (detalle) | Pulsa "Aplicar" (perfil incompleto — Hogar) | Advertencia con campos pendientes y acceso a completar perfil |
| Detalle del servicio | Pulsa dirección | App de Maps del dispositivo (Google Maps / Apple Maps) |
| Detalle del servicio | Pulsa "Reportar incidencia" | Formulario de reporte de incidencia |
| Detalle del servicio | Pulsa "Contacta con tu coordinador / empresa" | Información de teléfono de coordinación |
| Notificación push | Toca notificación | Pantalla específica relacionada via deeplink |
| Historial de notificaciones | Toca una notificación | Contenido relacionado via deeplink |
| Pantalla de fichaje | Pulsa "Reportar incidencia de fichaje" | Formulario de incidencia |
| Pantalla de fichaje | Pulsa "Solicitar ausencia" | Formulario de solicitud de ausencia |

---

## Criterios de Aceptación

### CA-001: Splash muestra logo y redirige ← HU-001
GIVEN la app se abre desde estado cerrado
WHEN se muestra la pantalla de splash
THEN se muestra el logo de la app sobre fondo de marca, y la app redirige automáticamente al login (o home si hay sesión) entre 2 y 3 segundos después de mostrar el splash, sin necesidad de interacción del usuario.

---

### CA-002: Splash redirige según estado de sesión ← HU-001
GIVEN la app se abre
WHEN se valida el estado de la sesión durante el splash
THEN si hay sesión válida se redirige a la home; si no hay sesión válida se redirige al login.

---

### CA-003: Onboarding se muestra solo una vez ← HU-002
GIVEN la trabajadora ha completado el onboarding al menos una vez
WHEN abre la app en sesiones posteriores
THEN el onboarding no se vuelve a mostrar.

---

### CA-004: Onboarding solicita permiso de notificaciones antes del onboarding ← HU-002
GIVEN la trabajadora acaba de hacer login por primera vez
WHEN se inicia el flujo de onboarding
THEN la app solicita permiso de notificaciones push antes de mostrar las pantallas de onboarding.

---

### CA-005: Onboarding solicita permiso de ubicación ← HU-002
GIVEN la trabajadora está en el onboarding
WHEN llega el paso de permisos
THEN la app solicita permiso de ubicación con una explicación clara de para qué se usa (fichaje).

---

### CA-006: Onboarding cubre ambos perfiles ← HU-002
GIVEN la trabajadora ve el onboarding
WHEN consulta el contenido
THEN el contenido es general y válido tanto para perfil Hogar como para perfil SAD.

---

### CA-007: Login con credenciales válidas ← HU-003
GIVEN la trabajadora introduce su email y contraseña correctos
WHEN pulsa "Iniciar sesión"
THEN la app verifica las credenciales, almacena la sesión de forma segura en el área de seguridad del dispositivo, y redirige a la pantalla principal sin necesidad de volver a hacer login hasta que la sesión expire.

---

### CA-008: Login con credenciales incorrectas ← HU-003
GIVEN la trabajadora introduce email o contraseña incorrectos
WHEN pulsa "Iniciar sesión"
THEN la app muestra un mensaje de error claro indicando que las credenciales son incorrectas; no redirige a la home.

---

### CA-009: Validación de formato de email en login ← HU-003
GIVEN la trabajadora está en la pantalla de login
WHEN introduce un email con formato inválido y pulsa "Iniciar sesión"
THEN la app muestra un error de validación en el campo email antes de enviar la solicitud al servidor.

---

### CA-010: Bloqueo temporal por intentos fallidos ← HU-003

> [INCOMPLETO] — Pendiente de gap [P-001]: el comportamiento observable del bloqueo (mensaje, duración, mecanismo de desbloqueo) y si es por dispositivo o por cuenta no están definidos. CA no puede completarse hasta resolver el gap.

---

### CA-011: Sesión persistente al abrir la app ← HU-003
GIVEN la trabajadora tiene una sesión activa almacenada y no han pasado 30 días sin usar la app
WHEN abre la app
THEN la app valida la sesión y redirige directamente a la home sin mostrar la pantalla de login.

---

### CA-012: Sesión expirada redirige al login ← HU-003
GIVEN la trabajadora tiene una sesión almacenada que ha expirado (más de 30 días sin uso o token revocado)
WHEN abre la app
THEN la app detecta que la sesión no es válida y muestra la pantalla de login.

---

### CA-013: Múltiples errores de sesión muestran login una sola vez ← HU-003
GIVEN la sesión ha expirado mientras la trabajadora tiene la app abierta con múltiples operaciones en curso
WHEN el servidor responde con "sesión inválida" a cualquiera de esas operaciones
THEN se muestra la pantalla de login una única vez, se cancelan las operaciones pendientes y no se muestran múltiples diálogos de error superpuestos.

---

### CA-014: Activación de cuenta SAD — flujo pendiente ← HU-004

> [INCOMPLETO] — Pendiente de gap [P-007]: el flujo de activación (qué pantalla abre el enlace, qué introduce la trabajadora, destino tras completar) no está definido. CA no puede completarse hasta resolver el gap.

---

### CA-015: Registro Hogar — campos y validaciones ← HU-005
GIVEN la trabajadora Hogar está en la pantalla de registro
WHEN introduce su email y contraseña
THEN la app valida el formato del email y que la contraseña cumple los requisitos (mínimo 8 caracteres, al menos una mayúscula y un número) antes de enviar el formulario.

---

### CA-016: Registro Hogar — alta completada ← HU-005
GIVEN la trabajadora Hogar ha introducido datos válidos en el formulario de registro
WHEN pulsa "Registrarse"
THEN el alta se completa y la trabajadora inicia sesión directamente, llegando a su home.

---

### CA-017: Registro Hogar — errores de validación ← HU-005
GIVEN la trabajadora Hogar introduce datos con formato inválido en el registro
WHEN pulsa "Registrarse"
THEN la app muestra mensajes de error claros en los campos con problemas, sin enviar el formulario.

---

### CA-018: Home Hogar — accesos directos ← HU-007
GIVEN la trabajadora Hogar está en la home
WHEN la home se carga
THEN se muestran accesos directos a: Ofertas, Mi Disponibilidad, Perfil, Comunicación.

---

### CA-019: Home Hogar — porcentaje de completitud visible ← HU-007
GIVEN la trabajadora Hogar está en la home
WHEN la home se carga
THEN se muestra el indicador de porcentaje de completitud del perfil de forma visible para incentivar su cumplimentación.

---

### CA-020: Home SAD — servicio activo + siguiente ← HU-006
GIVEN la trabajadora SAD está en la home
WHEN la home se carga
THEN el bloque de servicios muestra como máximo el servicio activo y el siguiente servicio; si hay más, muestra el enlace "Ver más servicios".

---

### CA-021: Home SAD — llamamiento pendiente muy visible ← HU-006
GIVEN la trabajadora SAD tiene un llamamiento pendiente de respuesta
WHEN abre la home
THEN el llamamiento se muestra de forma muy visible con indicación de urgencia y cuenta atrás de caducidad; el CTA lleva al detalle del llamamiento (no permite aceptar/rechazar directamente desde la home).

---

### CA-022: Home SAD — estados de la home (pendiente) ← HU-006

> [INCOMPLETO] — Pendiente de gap [P-002]: los estados posibles de la home SAD y qué muestra la home en cada estado (sin servicios, con servicio activo, con próximo servicio, con llamamiento pendiente, con ambos simultáneamente, etc.) no están definidos. CAs de cada estado no pueden completarse hasta resolver el gap.

---

### CA-023: Home SAD — documentación pendiente de firma ← HU-006
GIVEN la trabajadora SAD tiene documentación pendiente de firma
WHEN abre la home
THEN se muestra un badge/contador destacado para documentación pendiente de firma como elemento de alta prioridad.

---

### CA-024: Home SAD — bloque "Últimos avisos" ← HU-006
GIVEN la trabajadora SAD está en la home
WHEN la home se carga
THEN se muestra el bloque "Últimos avisos" con 2-3 items y acceso al listado completo.

---

### CA-025: Home — nombre y foto en cabecera ← HU-007 / HU-006
GIVEN la trabajadora (Hogar o SAD) está en la home
WHEN la home se carga
THEN se muestra el nombre de la trabajadora y su foto de perfil (o placeholder si no tiene foto) en la cabecera.

---

### CA-026: Home — pull-to-refresh ← HU-007 / HU-006
GIVEN la trabajadora (Hogar o SAD) está en la home
WHEN realiza un gesto de pull-to-refresh
THEN la home actualiza los datos mostrados.

---

### CA-027: Home — badges en accesos directos ← HU-007 / HU-006
GIVEN hay mensajes no leídos o acciones pendientes
WHEN la trabajadora ve la home
THEN los accesos directos correspondientes muestran un badge o contador.

---

### CA-028: Tablón — listado de comunicados diferenciado ← HU-008
GIVEN la trabajadora accede al tablón de anuncios
WHEN la lista se carga
THEN se muestran comunicados diferenciando entre contenidos fijos (protocolo, calendario laboral, PRL, documentos de referencia permanente) y comunicaciones variables (recordatorios, campañas, novedades); el backoffice puede fijar contenidos importantes en la parte superior.

---

### CA-029: Tablón — detalle y marcar como leído ← HU-008
GIVEN la trabajadora toca un comunicado en la lista
WHEN abre el detalle
THEN se muestra el título, fecha, texto completo, imágenes y adjuntos si los hay; el comunicado queda marcado como leído automáticamente.

---

### CA-030: Tablón — indicador de no leído ← HU-008
GIVEN hay comunicados no leídos
WHEN la trabajadora ve el tablón o el menú/tab correspondiente
THEN se muestra un badge indicando contenido nuevo no leído.

---

### CA-031: Mensajes del sistema — lista con criticidad ← HU-009
GIVEN la trabajadora accede a los mensajes del sistema
WHEN la lista se carga
THEN los mensajes de criticidad alta se muestran primero y de forma diferenciada; los de criticidad normal aparecen debajo.

---

### CA-032: Mensajes del sistema — borrar y marcar como leído ← HU-009
GIVEN la trabajadora está en los mensajes del sistema
WHEN toca un mensaje
THEN se muestra el contenido completo con adjuntos si los hay; el mensaje queda marcado como leído automáticamente; la trabajadora tiene opción de borrar el mensaje.

---

### CA-033: Mensajes del sistema — sin opción de respuesta ← HU-009
GIVEN la trabajadora está en el detalle de un mensaje del sistema
WHEN ve las opciones disponibles
THEN no existe botón de redactar respuesta; los mensajes son de solo lectura.

---

### CA-034: Listado de servicios — agrupado por estado ← HU-011
GIVEN la trabajadora SAD accede a "Mis Servicios"
WHEN la lista se carga
THEN los servicios aparecen agrupados en tres grupos: Activos, Próximos, Completados; con información clave de cada uno (nombre/código del cliente, dirección, fecha/hora, tipo).

---

### CA-035: Listado de servicios — distinción recurrente/puntual ← HU-011
GIVEN la trabajadora SAD ve la lista de servicios
WHEN revisa las tarjetas de servicio
THEN hay distinción visual entre servicios recurrentes (sin fecha de fin) y puntuales (con fecha de inicio y fin definidas).

---

### CA-036: Detalle del servicio — información básica y del cliente ← HU-010
GIVEN la trabajadora SAD toca un servicio en la lista
WHEN se abre el detalle del servicio
THEN se muestra la información básica del servicio (código, tipo, fechas, horario) y la información del cliente (nombre, dirección, edad); la visibilidad de determinados campos del cliente es controlable desde backoffice.

---

### CA-037: Detalle del servicio — datos de salud pendientes ← HU-010

> [INCOMPLETO] — Pendiente de gap [P-003]: qué datos de salud del cliente (si alguno) puede ver la trabajadora no está definido. CA no puede completarse hasta resolver el gap.

---

### CA-038: Detalle del servicio — dirección abre Maps ← HU-010
GIVEN la trabajadora SAD está en el detalle de un servicio
WHEN toca la dirección del cliente
THEN la app de Maps del dispositivo (Google Maps o Apple Maps, según el dispositivo) se abre con la dirección del servicio. No hay mapa embebido en la pantalla de detalle.

---

### CA-039: Detalle del servicio — plan de cuidados y tareas ← HU-010
GIVEN la trabajadora SAD está en el detalle de un servicio
WHEN consulta el plan de cuidados
THEN se muestra el listado descriptivo de tareas (sin checklist); la trabajadora no puede editarlo.

---

### CA-040: Detalle del servicio — CTA de contacto coordinador ← HU-010
GIVEN la trabajadora SAD está en el detalle de un servicio
WHEN ve la pantalla de detalle
THEN se muestra de forma prominente un CTA "Contacta con tu coordinador / empresa" con el teléfono de coordinación.

---

### CA-041: Detalle del servicio — accesos rápidos a fichaje e incidencias ← HU-010
GIVEN la trabajadora SAD está en el detalle de un servicio
WHEN ve la pantalla de detalle
THEN hay acceso directo para fichar entrada/salida y para reportar incidencia del servicio.

---

### CA-042: Notas de servicio — lista cronológica y añadir nota ← HU-013
GIVEN la trabajadora SAD accede a las notas de un servicio
WHEN ve la pantalla de notas
THEN se muestra la lista cronológica de notas con autora, fecha/hora, contenido y adjuntos; hay opción de añadir una nueva nota con texto multilínea y adjuntos (fotos o documentos); la nota se puede categorizar como: Evolución, Tareas, Incidencias, Otras.

---

### CA-043: Notas de servicio — borrar nota propia ← HU-013
GIVEN la trabajadora SAD ve una nota que ha creado ella misma
WHEN selecciona la opción de borrar
THEN la nota desaparece de la lista (borrado suave para auditoría). Las notas de otras autoras no tienen opción de borrar.

---

### CA-044: Llamamientos — lista con estados ← HU-012
GIVEN la trabajadora SAD accede al listado de llamamientos
WHEN la lista se carga
THEN se muestran todas las llamadas de servicio recibidas con estado (pendiente, aceptada, rechazada, caducada/desactivada) e información básica (código de servicio, fecha/hora, ubicación, urgencia).

---

### CA-045: Llamamientos — cuenta atrás para pendientes ← HU-012
GIVEN la trabajadora SAD tiene un llamamiento con estado "pendiente"
WHEN ve la lista o el detalle del llamamiento
THEN se muestra una cuenta atrás visual del tiempo restante para responder.

---

### CA-046: Llamamientos — bloqueo de navegación en detalle ← HU-012
GIVEN la trabajadora SAD entra al detalle de un llamamiento pendiente
WHEN intenta navegar hacia atrás sin haber tomado una decisión
THEN la navegación hacia atrás queda bloqueada hasta que acepte o rechace el llamamiento.

---

### CA-047: Llamamientos — aceptar con firma digital ← HU-012
GIVEN la trabajadora SAD está en el detalle de un llamamiento pendiente y pulsa aceptar
WHEN se muestra el diálogo de aceptación
THEN la trabajadora debe firmar digitalmente con el dedo para confirmar la aceptación; [PENDIENTE P-008: textos legales del diálogo de aceptación].

---

### CA-048: Llamamientos — rechazar con motivo y firma digital ← HU-012
GIVEN la trabajadora SAD está en el detalle de un llamamiento pendiente y pulsa rechazar
WHEN se muestra el diálogo de rechazo
THEN la trabajadora debe seleccionar un motivo (No disponible, Demasiado lejos, Motivos personales, Otros — con campo de texto) y firmar digitalmente con el dedo; [PENDIENTE P-008: textos legales del diálogo de rechazo].

---

### CA-049: Llamamientos — caducado sin respuesta (pendiente) ← HU-012

> [INCOMPLETO] — Pendiente de gap [P-004]: comportamiento cuando el llamamiento caduca sin respuesta (estado, consecuencias, notificación) no definido.

---

### CA-050: Llamamientos — desactivado cuando acepta otra trabajadora ← HU-012
GIVEN otro compañero ha aceptado un llamamiento al que la trabajadora también tenía acceso
WHEN la trabajadora ve su lista de llamamientos
THEN ese llamamiento aparece como desactivado/no disponible.

---

### CA-051: Nuevo servicio asignado (contrato indefinido) — notificación y confirmación ← HU-014
GIVEN la trabajadora SAD con contrato indefinido recibe un nuevo servicio asignado
WHEN llega la notificación push
THEN la notificación tiene deeplink al detalle del servicio; al abrir el detalle, se registra que la trabajadora ha recibido/visto la asignación; el nuevo servicio aparece en la home de forma diferenciada de los llamamientos.

---

### CA-052: Nuevo servicio asignado — generar incidencia si no puede atender ← HU-014
GIVEN la trabajadora SAD con contrato indefinido está en el detalle de un nuevo servicio asignado
WHEN decide que no puede atender el servicio
THEN puede generar una incidencia para comunicarlo a coordinación (no es un rechazo formal).

---

### CA-053: Fichaje — botón activo solo 30 minutos antes ← HU-018
GIVEN la trabajadora SAD tiene un servicio programado
WHEN consulta el botón de fichaje antes de la ventana de 30 minutos previos al inicio
THEN el botón aparece deshabilitado con indicación visual del tiempo restante ("Disponible en X min").

---

### CA-054: Fichaje — habilitar y estados dinámicos ← HU-018
GIVEN la trabajadora SAD está dentro de la ventana de fichaje (30 minutos antes del inicio del servicio)
WHEN consulta el botón de fichaje
THEN el botón muestra "Fichar entrada" y está habilitado; los estados posibles del botón son: "Disponible en X min", "Fichar entrada", "Fichada · en servicio", "Fichar salida", "Servicio finalizado".

---

### CA-055: Fichaje — captura de geolocalización ← HU-018
GIVEN la trabajadora SAD pulsa "Fichar entrada" o "Fichar salida"
WHEN se ejecuta el fichaje
THEN la app captura las coordenadas GPS del dispositivo en ese momento.

---

### CA-056: Fichaje — advertencia de baja precisión ← HU-018
GIVEN la trabajadora SAD inicia el fichaje y la precisión del GPS es baja
WHEN la app detecta precisión insuficiente
THEN muestra una advertencia; espera máximo 2 segundos y permite continuar igualmente (el fichaje no queda bloqueado por ubicación).

---

### CA-057: Fichaje — confirmación de salida ← HU-018
GIVEN la trabajadora SAD pulsa "Fichar salida"
WHEN se muestra el diálogo de confirmación
THEN la trabajadora debe confirmar la salida; tras confirmar, el fichaje queda registrado.

---

### CA-058: Fichaje — aviso si no se ficha salida ← HU-018
GIVEN la trabajadora SAD ha fichado entrada en un servicio y el servicio ha terminado sin fichar salida
WHEN la trabajadora usa la app
THEN se muestra un aviso visible (banner o notificación in-app) recordando fichar la salida; este aviso no bloquea la navegación ni el acceso al resto de la app.

---

### CA-059: Fichaje — sin bloqueo entre servicios del mismo día ← HU-018
GIVEN la trabajadora SAD tiene dos servicios en el mismo día (mañana y tarde)
WHEN ficha salida del primero
THEN puede fichar entrada del segundo de forma independiente, sin bloqueo entre servicios.

---

### CA-060: Historial de fichajes — agrupado por servicio y día ← HU-033
GIVEN la trabajadora SAD accede al historial de fichajes
WHEN la lista se carga
THEN los registros aparecen agrupados por servicio y por días, con fecha, hora de entrada, hora de salida y duración de cada registro. No se muestran conteos de horas extra ni diferencias respecto a horas contratadas.

---

### CA-061: Historial de fichajes — filtros ← HU-033
GIVEN la trabajadora SAD está en el historial de fichajes
WHEN aplica filtros
THEN puede filtrar por rango de fechas y por servicio.

---

### CA-062: Reportar incidencia — formulario completo ← HU-021
GIVEN la trabajadora SAD accede al formulario de reporte de incidencia
WHEN completa el formulario
THEN puede seleccionar el tipo (Salud del cliente, Seguridad, Material/equipamiento, Incidencia de fichaje / No asistencia, Otros), seleccionar servicio relacionado, introducir descripción (obligatorio, mínimo 20 caracteres), adjuntar hasta 5 fotos y hasta 3 documentos de forma opcional.

---

### CA-063: Reportar incidencia — confirmación y visibilidad ← HU-021
GIVEN la trabajadora SAD envía un reporte de incidencia válido
WHEN la solicitud se procesa
THEN la app muestra confirmación de envío; la incidencia es inmediatamente visible para las coordinadoras.

---

### CA-064: Historial de incidencias ← HU-034
GIVEN la trabajadora SAD accede al historial de incidencias
WHEN la lista se carga
THEN las incidencias aparecen en orden cronológico inverso con número, tipo, fecha y estado (Reportada, En revisión, Resuelta, Cerrada); puede filtrar por estado, por rango de fechas y buscar por número o descripción; al tocar una incidencia ve los detalles completos y los comentarios de las coordinadoras.

---

### CA-065: Navegar ofertas — lista con filtros ← HU-015
GIVEN la trabajadora Hogar accede a la sección de ofertas
WHEN la lista se carga
THEN se muestran las ofertas disponibles en formato de tarjeta con: título del trabajo, ubicación (código postal/ciudad), horario y tarifa horaria; puede filtrar por zona, horario, rango de fecha de inicio; puede ordenar por más recientes, ubicación más cercana o tarifa más alta.

---

### CA-066: Navegar ofertas — badge "Nuevo" ← HU-015
GIVEN hay ofertas publicadas en las últimas 48 horas
WHEN la trabajadora Hogar ve el listado
THEN esas ofertas muestran la insignia "Nuevo".

---

### CA-067: Navegar ofertas — estado vacío ← HU-015
GIVEN la trabajadora Hogar aplica filtros que no devuelven resultados
WHEN la lista se actualiza
THEN se muestra el mensaje "No se han encontrado ofertas con los filtros actuales" con un botón para limpiar filtros (asunción P-011).

---

### CA-068: Solicitar oferta — confirmación y prevención de duplicados ← HU-016
GIVEN la trabajadora Hogar pulsa "Aplicar" en una oferta
WHEN se muestra el diálogo de confirmación
THEN aparece el resumen de la oferta; al confirmar, la solicitud se envía con un solo toque, se muestra mensaje de éxito y la trabajadora recibe notificación de confirmación. No se puede enviar solicitud duplicada a la misma oferta.

---

### CA-069: Mis solicitudes — lista y estados ← HU-017
GIVEN la trabajadora Hogar accede a "Mis solicitudes"
WHEN la lista se carga
THEN las solicitudes aparecen en orden cronológico inverso con título de la oferta, ubicación, fecha de solicitud y estado (Pendiente, En revisión, Aceptada, Rechazada, Oferta cerrada); puede filtrar por estado; las solicitudes aceptadas tienen distinción visual.

---

### CA-070: Mis solicitudes — retirar solicitud ← HU-017
GIVEN la trabajadora Hogar tiene una solicitud con estado "Pendiente"
WHEN pulsa la opción de retirar solicitud
THEN la solicitud queda retirada y desaparece de las pendientes activas.

---

### CA-071: Disponibilidad — vista semanal ← HU-026
GIVEN la trabajadora (Hogar o SAD) accede a "Mi Disponibilidad"
WHEN la pantalla se carga
THEN se muestra una vista semanal (Lun–Dom) con los slots de disponibilidad existentes como bloques horarios con color diferenciado por tipo: Disponible, No disponible, Activa (solo lectura). En la cabecera se muestran las horas trabajadas vs. horas de contrato de forma prominente.

---

### CA-072: Disponibilidad — crear slot con franja rápida ← HU-026
GIVEN la trabajadora selecciona un día en el calendario de disponibilidad
WHEN pulsa una franja predefinida (Mañana, Tarde, Noche, Interna, Finde)
THEN se crea inmediatamente un slot de tipo "Disponible" con el rango horario de esa franja para el día seleccionado. La franja Madrugada no está disponible.

---

### CA-073: Disponibilidad — crear slot personalizado ← HU-026
GIVEN la trabajadora selecciona un día en el calendario de disponibilidad
WHEN usa el formulario de slot personalizado
THEN puede introducir hora de inicio y hora de fin, y elegir el tipo (Disponible o No disponible); se permiten solapamientos entre slots de distinto tipo; no se permiten solapamientos entre slots del mismo tipo (la API devuelve error si ocurre).

---

### CA-074: Disponibilidad — editar y borrar slot ← HU-026
GIVEN la trabajadora toca un slot de tipo "Disponible" o "No disponible"
WHEN selecciona editar o eliminar
THEN puede modificar la hora inicio/fin o el tipo, o eliminar el slot; los cambios se guardan de forma inmediata al confirmar.

---

### CA-075: Disponibilidad — slot Activa es de solo lectura ← HU-026
GIVEN la trabajadora toca un slot de tipo "Activa"
WHEN interacciona con él
THEN se muestra solo información del slot; no hay opción de editar ni eliminar.

---

### CA-076: Disponibilidad — recordatorio si no se actualiza ← HU-026
GIVEN la trabajadora no ha actualizado su disponibilidad en 30 días
WHEN el sistema detecta la inactividad
THEN envía una notificación de recordatorio a la trabajadora.

---

### CA-077: Solicitar ausencia — formulario completo ← HU-020
GIVEN la trabajadora SAD accede al formulario de solicitud de ausencia
WHEN completa el formulario
THEN puede seleccionar el tipo (Vacaciones, Permiso personal, Baja médica, Baja voluntaria, Asuntos propios, Otros), el rango de fechas con opción de medio día en fechas de inicio/fin, y el motivo/descripción (obligatorio en los tipos que lo requieren); se muestra el saldo de vacaciones disponible; si las fechas conflictan con servicios asignados, se muestra una advertencia.

---

### CA-078: Solicitar ausencia — certificado médico obligatorio para baja > 3 días ← HU-020
GIVEN la trabajadora SAD solicita una baja médica de más de 3 días
WHEN completa el formulario
THEN el campo de adjuntar certificado médico es obligatorio para enviar la solicitud.

---

### CA-079: Historial de ausencias — lista, contadores y cancelar ← HU-019
GIVEN la trabajadora SAD accede al historial de ausencias
WHEN la pantalla se carga
THEN las ausencias aparecen en orden cronológico inverso con tipo, fechas, recuento de días y estado (Pendiente, Aprobada, Rechazada, Cancelada); se muestran los contadores por tipo de ausencia (asignación anual total, días utilizados, días pendientes de aprobación, días disponibles); puede filtrar por estado, tipo de ausencia y año; puede cancelar solicitudes con estado "Pendiente".

---

### CA-080: Contadores de vacaciones — cómputo pendiente ← HU-019

> [INCOMPLETO] — Pendiente de gap [P-005]: el criterio de cómputo de vacaciones (días naturales o días laborables) no está definido. El CA de contadores no puede completarse hasta resolver el gap.

---

### CA-081: Ver perfil — secciones y campos ← HU-022
GIVEN la trabajadora accede a su perfil
WHEN la pantalla se carga
THEN se muestran las secciones: Información Personal (nombre, email, teléfono, dirección — editable, fecha de nacimiento, DNI/NIE), Profesional (experiencia, especializaciones, certificaciones), Educación (títulos, cursos), Idiomas (idioma + nivel); se muestra el indicador de porcentaje de completitud del perfil.

---

### CA-082: Ver perfil — datos core de solo lectura; dirección editable ← HU-022
GIVEN la trabajadora está en la pantalla de perfil
WHEN revisa los campos
THEN los datos core (nombre, apellidos, DNI/NIE) son de solo lectura; la dirección de domicilio tiene botón de edición; los demás campos editables tienen botón de edición por sección.

---

### CA-083: Ver perfil — DNI/NIE con fecha de vencimiento y propuesta de cambio ← HU-022
GIVEN la trabajadora está en la pantalla de perfil, sección DNI/NIE
WHEN revisa el campo
THEN se muestra la fecha de vencimiento del DNI/NIE; hay un flujo para "proponer nueva fecha + adjuntar documento" que el backoffice valida; la trabajadora no puede editar el dato directamente.

---

### CA-084: Ver perfil — tipo de contrato SAD (pendiente) ← HU-022

> [INCOMPLETO] — Pendiente de gap [P-006]: qué tipo(s) de contrato se muestran en el perfil SAD (dimensión jurídica, de jornada, o ambas) no está definido.

---

### CA-085: Perfil Hogar — advertencia al aplicar con perfil incompleto ← HU-022
GIVEN la trabajadora Hogar tiene campos obligatorios del perfil sin completar
WHEN intenta aplicar a una oferta
THEN la app muestra una advertencia o bloqueo informando de los campos obligatorios pendientes, con acceso directo a completarlos.

---

### CA-086: Foto de perfil — subir y cambiar ← HU-023
GIVEN la trabajadora está en la pantalla de foto de perfil
WHEN toca la foto o el placeholder
THEN puede elegir foto de galería o hacer una nueva foto; puede recortarla en relación de aspecto cuadrada antes de subir; la app muestra el progreso de subida; la nueva foto se refleja en toda la app inmediatamente.

---

### CA-087: Documentos — lista por categorías ← HU-024
GIVEN la trabajadora accede a la sección de documentos
WHEN la pantalla se carga
THEN se muestran los documentos organizados en dos categorías: Documentación personal y Documentación laboral; las carpetas y tipos dentro de cada categoría son configurables desde backoffice.

---

### CA-088: Documentos personales — subir y reemplazar ← HU-024
GIVEN la trabajadora está en la sección de documentación personal
WHEN sube o reemplaza un documento
THEN puede seleccionar el tipo, elegir un archivo del dispositivo o hacer una foto (formatos: PDF, DOC, DOCX, JPG, PNG), añadir descripción opcional; el documento queda disponible en la app. No puede eliminar documentos personales, solo reemplazar.

---

### CA-089: Documentos laborales — solo lectura y firma ← HU-024
GIVEN la trabajadora está en la sección de documentación laboral
WHEN revisa sus documentos laborales
THEN puede consultar y descargar los documentos; no puede subir ni eliminar documentos laborales; si un documento requiere firma, puede firmarlo digitalmente; los documentos pendientes de firma generan badge/aviso en la sección y en la home.

---

### CA-090: Firma digital — captura y almacenamiento ← HU-024
GIVEN la trabajadora accede al lienzo de firma digital
WHEN dibuja su firma con el dedo o stylus
THEN puede borrar/reiniciar la firma, previsualizar antes de guardar, y guardar la firma; la firma queda almacenada en el perfil y disponible para futuras firmas de documentos.

---

### CA-091: Estado del contrato SAD (pendiente) ← HU-025

> [INCOMPLETO] — Pendiente de gap [P-006]: qué tipo(s) de contrato se muestran en "Estado del contrato" (dimensión jurídica, de jornada, o ambas) no está definido.

---

### CA-092: Estado del contrato SAD — datos disponibles ← HU-025
GIVEN la trabajadora SAD accede a "Estado del contrato"
WHEN la pantalla se carga
THEN se muestran la fecha de inicio del contrato y el número de empleada; hay un enlace para descargar el PDF del contrato actual; la información es de solo lectura.

---

### CA-093: Nueva conversación — asunto predefinido ← HU-027
GIVEN la trabajadora (Hogar o SAD) pulsa "Nueva conversación"
WHEN se muestra la selección de asuntos
THEN puede elegir entre: Vacaciones/Ausencia, Nómina/Facturación, Sobre un servicio, Documentación, Consulta general, Otros; puede enlazar contexto (servicio u oferta relacionados) opcionalmente; debe escribir un primer mensaje para crear la conversación.

---

### CA-094: Hilo de conversación — mensajes en tiempo real ← HU-027
GIVEN la trabajadora tiene una conversación abierta
WHEN coordinación envía un mensaje
THEN el mensaje aparece en el hilo en tiempo real sin necesidad de recargar la pantalla.

---

### CA-095: Hilo de conversación — conversación cerrada ← HU-027 / HU-028
GIVEN una conversación ha sido cerrada por coordinación
WHEN la trabajadora accede al hilo
THEN el campo de entrada está oculto, se muestra el aviso "Conversación cerrada", y puede consultar el historial completo en modo lectura.

---

### CA-096: Listado de conversaciones ← HU-028
GIVEN la trabajadora accede al listado de conversaciones
WHEN la lista se carga
THEN las conversaciones aparecen en orden cronológico inverso (por último mensaje) con asunto, previsualización del último mensaje y marca de tiempo; las conversaciones con mensajes no leídos están diferenciadas visualmente (bold, badge); las conversaciones cerradas tienen indicador diferenciado (etiqueta "Cerrada" o icono de candado).

---

### CA-097: Borrar conversación ← HU-028
GIVEN la trabajadora está en el listado de conversaciones
WHEN selecciona la opción de borrar una conversación
THEN se muestra un diálogo de confirmación; al confirmar, la conversación queda borrada independientemente del estado de lectura de los mensajes (asunción P-012).

---

### CA-098: Cerrar sesión — confirmación y limpieza ← HU-029
GIVEN la trabajadora accede a la opción de cerrar sesión
WHEN pulsa "Cerrar sesión"
THEN se muestra un diálogo de confirmación; al confirmar, se borran todos los tokens y datos de sesión almacenados en el dispositivo, se invalida el token en el backend y se redirige a la pantalla de login.

---

### CA-099: Notificaciones push — solicitud de permiso ← HU-030
GIVEN la trabajadora acaba de hacer login por primera vez
WHEN se inicia el flujo de onboarding
THEN la app solicita permiso de notificaciones push antes de mostrar las pantallas de onboarding; el token del dispositivo queda vinculado al usuario concreto.

---

### CA-100: Notificaciones push — recepción en todos los estados ← HU-030
GIVEN la trabajadora tiene permiso de notificaciones activado
WHEN llega una notificación
THEN la notificación se recibe y muestra independientemente de si la app está en primer plano (alerta dentro de la app), segundo plano (notificación del sistema) o cerrada (notificación del sistema); la notificación incluye título, cuerpo e icono; tocar la notificación abre la app en la pantalla específica relacionada vía deeplink.

---

### CA-101: Historial de notificaciones ← HU-031
GIVEN la trabajadora accede al historial de notificaciones (asunción P-009)
WHEN la pantalla se carga
THEN se muestra un listado de notificaciones recibidas con título, cuerpo y fecha; tocar una notificación abre el contenido relacionado vía deeplink; existe la opción de marcar todas como leídas; no se pueden borrar notificaciones individuales desde el historial.

---

### CA-102: Acceso revocado — pantalla informativa (SAD) ← HU-032
GIVEN una trabajadora SAD intenta acceder con credenciales válidas pero su cuenta ha sido suspendida, dada de baja o desactivada
WHEN el backend devuelve el estado de cuenta revocada durante la autenticación
THEN se muestra la pantalla de acceso revocado con el mensaje "Ya no tienes permisos para acceder a esta aplicación", información de contacto o soporte, y sin posibilidad de navegar a ninguna sección de la app; no se almacenan tokens en este estado.

---

### CA-103: Recuperar contraseña — flujo completo ← HU-035
GIVEN la trabajadora pulsa "¿Olvidaste tu contraseña?" en el login
WHEN introduce su email en la pantalla de recuperación
THEN la app muestra confirmación del envío del email sin revelar si el email existe en el sistema; el enlace recibido permite establecer una nueva contraseña que cumple los mismos requisitos que el registro (mínimo 8 caracteres, al menos una mayúscula y un número); si la cuenta está dada de baja, el enlace muestra la pantalla de acceso revocado.

---

### CA-104: Notificaciones automáticas del sistema ← HU-030
GIVEN el sistema detecta condiciones que requieren recordatorio
WHEN se cumplen las condiciones
THEN se envían automáticamente: recordatorio de disponibilidad si no se actualiza en 30 días; aviso de caducidad de documento 30 días antes; recordatorio de servicio 1 día antes; recordatorio de fichar entrada N minutos después del inicio si no se ha fichado (N configurable); aviso de ausencia próxima 1 día antes.

---

### CA-105: Notificación de servicio próximo mañana — múltiples servicios ← HU-030
GIVEN la trabajadora tiene más de un servicio programado para mañana (asunción P-010)
WHEN el sistema envía las notificaciones de servicio próximo mañana
THEN se envía una notificación separada por cada servicio programado para el día siguiente, cada una con deeplink al detalle del servicio correspondiente.

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
- [ ] Textos legales de llamamientos revisados por legal ([P-008])
- [ ] Datos de salud y RGPD revisados por legal ([P-003])
- [ ] Tipo de contrato alineado con backend ([P-006])
- [ ] Flujo de activación SAD revisado con cliente ([P-007])
- [ ] Cómputo de vacaciones confirmado con cliente/legal ([P-005])
- [ ] Comportamiento bloqueo de login revisado con cliente ([P-001])
- [ ] Estados de home SAD definidos con cliente ([P-002])
- [ ] Comportamiento de llamamiento caducado revisado con legal ([P-004])

---

## Fuera de Alcance

- Autenticación biométrica (Face ID, huella digital)
- Autenticación de dos factores (2FA)
- Gestión activa de pagos/nóminas (el acceso de solo lectura a documentos de nómina está dentro del alcance como parte de Documentación laboral)
- Funciones sociales (perfiles públicos, valoraciones entre trabajadoras)
- Configuración de preferencias de notificaciones por tipo (previsto para una fase futura)
- Pantalla de historial de servicios completados (RF-3.5 del PRD): el historial completo de llamamientos con su resultado está incluido en el alcance; el historial de servicios completados con filtro por fechas y detalle de horas trabajadas no está incluido en este spec.

---

## Items pendientes

- [PENDIENTE] [P-001]: Comportamiento observable del bloqueo temporal de login por intentos fallidos (mensaje, duración, mecanismo de desbloqueo, alcance por dispositivo o cuenta).
- [PENDIENTE] [P-002]: Estados posibles de la home SAD (sin servicios, con servicio activo, con próximo servicio, con llamamiento pendiente, con combinaciones) y contenido de la home en cada estado.
- [PENDIENTE] [P-003]: Qué datos de salud del cliente puede ver la trabajadora SAD en el detalle del servicio tras la revisión RGPD con legal.
- [PENDIENTE] [P-004]: Comportamiento cuando un llamamiento caduca sin respuesta (estado registrado, consecuencias, notificación a la trabajadora).
- [PENDIENTE] [P-005]: Criterio de cómputo de vacaciones (días naturales o días laborables) y si aplica a otros tipos de ausencia.
- [PENDIENTE] [P-006]: Tipo(s) de contrato a mostrar en el perfil SAD y en "Estado del contrato" (Indefinido/Fijo Discontinuo, Tiempo completo/Tiempo parcial, o ambas dimensiones).
- [PENDIENTE] [P-007]: Flujo completo de activación de cuenta SAD (qué pantalla abre el enlace del email, campos que introduce la trabajadora, destino al completar la activación).
- [PENDIENTE] [P-008]: Textos legales definitivos para los diálogos de firma de aceptación y rechazo de llamamientos.
