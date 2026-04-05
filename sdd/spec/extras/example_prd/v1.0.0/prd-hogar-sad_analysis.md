# Análisis SDD: PRD Aplicaciones Móviles CUIDEO - Hogar & SAD

> **Generado por**: sdd-analyst (modo analyze)
> **Fecha**: 2026-04-02
> **Archivo origen**: prd-hogar-sad.md

---

## Leyenda de notación

| Código | Significado | Dónde aparece |
|--------|-------------|---------------|
| `[C-XXX]` | Contaminación técnica detectada | Sección Pureza |
| `[CA-XXX]` | Criterio de Aceptación problemático | Sección Testabilidad |
| `[P-XXX]` | Pregunta pendiente de validación con el cliente | Sección Puntos pendientes |
| `[CRÍTICO]` | Gap que impide completar las HUs afectadas — quedarán marcadas `[INCOMPLETO]` en el spec si no se responde | Sección Puntos pendientes |
| `[INFORMATIVO]` | Gap con asunción por defecto — se aplica automáticamente si no se responde | Sección Puntos pendientes |
| `_(pendiente)_` | Respuesta aún no proporcionada por el cliente | Campo "Respuesta" de cada gap |

---

## Estado general

> **REQUIERE_TRABAJO**
>
> El documento contiene información funcional rica y detallada, pero no está estructurado como Spec SDD: carece de Historias de Usuario formales, los Criterios de Aceptación no siguen el formato GIVEN/WHEN/THEN, hay contaminación técnica extensa (stack tecnológico, endpoints, especificaciones de plataforma) y varios puntos funcionales están explícitamente marcados como pendientes en el propio PRD. Antes de generar el Spec se deben responder los gaps CRÍTICOS y resolver las decisiones funcionales abiertas.

---

## Completitud: 3/8 elementos presentes

- [ ] **Actores** — parcial: se mencionan "trabajadora Hogar", "trabajadora SAD" y "coordinadora/backoffice" de forma dispersa, pero no existe una tabla formal de actores con sus capacidades en este producto
- [ ] **Historias de Usuario (Como/quiero/para que)** — ausente: el documento usa Requisitos Funcionales (RF) pero ninguno está expresado en formato "Como [actor] / quiero [acción] / para que [beneficio]"
- [ ] **Recorridos de Usuario** — parcial: algunos RF contienen descripción narrativa (p. ej. RF-3.4 llamamientos, RF-7.1 disponibilidad), pero no hay journeys completos paso a paso desde la perspectiva del actor para cada funcionalidad
- [ ] **Resultados y Éxito** — parcial: algunos CAs implican el estado de éxito, pero no hay una sección dedicada "¿cómo se ve terminado?" para cada flujo principal
- [x] **Instrucciones Inambiguas** — parcial: el documento tiene buen nivel de detalle en varios RF, pero contiene pendientes funcionales explícitos (RGPD en RF-3.2, tipo de contrato en RF-9.1/RF-9.5, vacaciones días naturales en RF-8.2, textos legales en RF-3.4) que generan ambigüedades reales
- [ ] **Criterios de Aceptación (GIVEN/WHEN/THEN)** — parcial: existen CAs numerados, pero ninguno usa el formato GIVEN/WHEN/THEN; varios son vagos o no verificables objetivamente
- [ ] **Checklist de Validación** — ausente
- [x] **Fuera de Alcance** — presente (sección "Fuera de Alcance - Posibles fases futuras")

> **Nota sobre Fuera de Alcance**: la sección existente contiene ítems funcionales válidos (autenticación biométrica, 2FA, modo offline) junto con contaminaciones técnicas que se detallan en la sección Pureza.

---

## Pureza: CONTAMINADO

El documento es un PRD técnico que mezcla extensamente decisiones de implementación con requisitos funcionales. Se listan las instancias más relevantes para el Spec.

#### [C-001] Stack tecnológico declarado en el cuerpo del PRD
- **Cita**: > "Arquitectura de doble perfil: Codebase única (KMM) que sirve dos aplicaciones de marca diferentes" (sección Puntos Clave) y toda la sección "Arquitectura del Sistema" con el diagrama KMM/API REST/Base de Datos
- **Problema**: Menciona el lenguaje/framework de implementación (Kotlin Multiplatform Mobile), el patrón de arquitectura (codebase compartida), y la plataforma de red (API RESTful, JSON). El Spec debe describir el comportamiento del sistema para el usuario, no cómo se construye.
- **Reescritura sugerida**: "El producto se presenta como dos aplicaciones de marca diferenciada (CUIDEO para perfil Hogar, Felizvita para perfil SAD) que comparten las mismas funcionalidades de base y adaptan su contenido al tipo de contrato de la trabajadora."
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-002] Autenticación basada en JWT / Token Sanctum
- **Cita**: > "Autenticación basada en JWT" (sección Backend) y "Token Sanctum con validez de 30 días" (RF-1.5, RNF-1.2)
- **Problema**: JWT y Sanctum son tecnologías de implementación. El Spec debe describir el comportamiento funcional de la sesión (cuándo expira, cuándo se cierra), no el mecanismo técnico que lo implementa.
- **Reescritura sugerida**: "La sesión se mantiene activa durante 30 días desde el último uso. Expira si la usuaria lleva 30 días sin acceder, cierra sesión explícitamente, o su cuenta es revocada por administración."
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-003] Almacenamiento seguro de tokens con referencia a plataformas específicas
- **Cita**: > "Tokens de acceso almacenados en almacenamiento seguro: iOS: Keychain / Android: EncryptedSharedPreferences / Android Keystore" (RNF-1.1 CA3) y "Almacenar tokens de forma segura (iOS Keychain / Android Keystore)" (RF-1.3 CA8)
- **Problema**: iOS Keychain, EncryptedSharedPreferences y Android Keystore son APIs específicas de plataforma. El Spec debe expresar el requisito funcional de seguridad, no la solución técnica.
- **Reescritura sugerida**: "Las credenciales de sesión se almacenan en el área de seguridad del dispositivo, protegidas contra acceso no autorizado por otras aplicaciones."
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-004] Firebase como servicio de notificaciones y mensajería
- **Cita**: > "Firebase Cloud Messaging (notificaciones push) / Firebase Realtime Database (mensajería) / Firebase Crashlytics (reporte de caídas) / Firebase Analytics (analítica básica)" (sección Integraciones Externas) y "Actualizaciones de mensajes en tiempo real (realtime database)" (RF-10.3 CA11) y "Firebase Crashlytics integrado" (RNF-5.1 CA1)
- **Problema**: Firebase es una elección tecnológica de implementación. El Spec debe describir las capacidades funcionales (recibir mensajes en tiempo real, recibir notificaciones push), no el proveedor que las soporta.
- **Reescritura sugerida**: "Los mensajes de chat se actualizan en tiempo real sin necesidad de recargar la pantalla. Las notificaciones push se entregan incluso cuando la app está en segundo plano o cerrada."
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-005] Especificación completa de endpoints de API
- **Cita**: Toda la sección "Especificación de la API" (líneas 191-327) y los bloques "Endpoints API Requeridos" al final de cada RF.
- **Problema**: Los endpoints, métodos HTTP, parámetros de body y rutas de API son detalles de integración técnica. En el Spec deben describirse los datos que el sistema obtiene o envía funcionalmente, no cómo se comunica con el backend.
- **Reescritura sugerida**: Los endpoints deben eliminarse del Spec. La información que aportan (qué datos consulta o envía el sistema para cada acción) puede describirse en las instrucciones inambiguas de cada funcionalidad.
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-006] Módulos técnicos de la arquitectura KMM
- **Cita**: > "Módulo de Red: Cliente API, gestión de solicitudes/respuestas / Módulo de Autenticación: Inicio de sesión, gestión de tokens, sesión..." (sección "Lógica de Negocio Compartida KMM")
- **Problema**: La descomposición en módulos de código (Módulo de Red, Módulo de Autenticación, etc.) es arquitectura técnica interna, no un requisito funcional.
- **Reescritura sugerida**: Esta sección debe eliminarse del Spec íntegramente. La arquitectura de módulos pertenece al Plan.
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-007] Bundle IDs, colores hexadecimales y versiones de sistema operativo
- **Cita**: > "Bundle ID: es.cuideo.hogar (iOS) / es.cuideo.hogar (Android) / Primary Color: Azul (#0066CC o especificado por cliente)" (RF-12.1 CA1) y "iOS 16+ (App Store) / Android 8+ / API Level 26 (Google Play)" (RF-12.1 CA3) y "Tamaño mínimo del área táctil: 44x44 pts (iOS) / 48x48 dp (Android)" (RNF-2.2 CA2)
- **Problema**: Los Bundle IDs, colores hex, versiones mínimas de OS y valores en puntos/dp son especificaciones técnicas de plataforma. El color de marca puede expresarse funcionalmente; los requisitos de OS son restricciones técnicas del Plan.
- **Reescritura sugerida**: "La app CUIDEO tiene identidad visual azul; la app Felizvita tiene identidad visual verde. Los colores exactos serán provistos por el cliente en las guías de marca." (Los Bundle IDs y versiones de OS van al Plan.)
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-008] Compresión de imágenes y tamaños de archivo como CAs funcionales
- **Cita**: > "Compresión automática" (RF-9.2 CA5, RF-5.1 CA7) y "Tamaño máximo de archivo 5MB" (RF-9.2 CA6) y "Mostrar tamaño estimado de subida antes de enviar" (RF-5.1 CA6)
- **Problema**: Los límites de tamaño de archivo y la compresión son restricciones técnicas de implementación. El requisito funcional es que el usuario pueda adjuntar archivos de forma práctica; los límites técnicos van al Plan.
- **Reescritura sugerida**: "La trabajadora puede adjuntar fotos y documentos. El sistema informa si un archivo no puede enviarse antes de intentar la subida."
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-009] TLS 1.2+ y anclaje de certificados como CAs funcionales
- **Cita**: > "Toda la comunicación con la API sobre HTTPS (TLS 1.2+) / Anclaje de certificados para endpoints de la API" (RNF-1.1 CA1/CA2)
- **Problema**: TLS 1.2+ y certificate pinning son requisitos de seguridad técnicos de red. El requisito funcional es que la comunicación sea segura y no interceptable.
- **Reescritura sugerida**: "Toda la comunicación de la app con el servidor está cifrada y protegida contra interceptación."
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-010] "Retroalimentación visual clara para todas las interacciones (<100 ms)" y métricas de rendimiento
- **Cita**: > "Retroalimentación visual clara para todas las interacciones (<100 ms) / Indicadores de carga para operaciones >500 ms" (RNF-2.1 CA2/CA5)
- **Problema**: Los valores en milisegundos son requisitos de rendimiento técnico. El requisito funcional es que el usuario reciba confirmación visual inmediata de sus acciones y que las operaciones largas muestren un indicador de progreso.
- **Reescritura sugerida**: "Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse."
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-011] "La arquitectura de la aplicación admite múltiples idiomas" (RNF-3.1 CA1)
- **Cita**: > "La arquitectura de la aplicación admite múltiples idiomas"
- **Problema**: "Arquitectura de la aplicación" es lenguaje técnico. El requisito funcional es que la app pueda mostrarse en varios idiomas.
- **Reescritura sugerida**: "La app puede mostrarse en múltiples idiomas. El lanzamiento inicial es en castellano; la estructura permite añadir catalán, inglés y francés en versiones futuras."
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

#### [C-012] Fuera de Alcance con exclusiones técnicas
- **Cita**: > "Detección de GPS simulado / Modo offline con sincronización / Eventos de analytics personalizados (solo Firebase out-of-the-box)"
- **Problema**: "Detección de GPS simulado", "sincronización offline" y "Firebase out-of-the-box" son exclusiones técnicas de implementación, no funcionales.
- **Reescritura sugerida**: Eliminar estas tres líneas del Fuera de Alcance del Spec. Las exclusiones técnicas van al Plan. Pueden reescribirse funcionalmente si procede: p. ej. "No se detectarán intentos de falsificar la ubicación" (si es un requisito funcional de seguridad, debe estar en scope, no fuera).
- **Acción**: `[x] ACEPTAR` · `[ ] EDITAR` · `[ ] RECHAZAR (justificar)`

---

## Testabilidad: REQUIERE_MEJORA

Ningún CA en el documento usa el formato GIVEN/WHEN/THEN. Se señalan los casos más representativos que requieren reformulación. En el Spec generado todos los CAs deberán expresarse en este formato.

#### [CA-001] RF-1.0 CA2 — Duración de splash vaga
- **CA actual**: "Duración de 2-3 segundos antes de redirigir automáticamente"
- **Problema**: No es verificable objetivamente: ¿se mide con la app en frío, en caliente? ¿El redireccionamiento ocurre exactamente al límite o con margen?
- **Sugerencia de reformulación**:
  ```
  GIVEN la app se abre desde estado cerrado
  WHEN se muestra la pantalla de splash
  THEN la app redirige automáticamente al login (o home si hay sesión) entre 2 y 3 segundos después de mostrar el splash, sin necesidad de interacción del usuario
  ```

---

#### [CA-002] RF-1.3 CA4 — Bloqueo temporal con N no definida funcionalmente
- **CA actual**: "Bloqueo temporal tras N intentos fallidos (N configurable en servidor)"
- **Problema**: El valor N no está definido en el documento ni se especifica qué significa "bloqueo temporal" para el usuario (¿mensaje de error? ¿tiempo de espera? ¿desbloqueo por email?).
- **Sugerencia de reformulación** (pendiente de respuesta a [P-001]):
  ```
  GIVEN la trabajadora ha fallado N intentos de login consecutivos (N definido por backend)
  WHEN intenta iniciar sesión una vez más
  THEN se muestra un mensaje informando del bloqueo temporal y el tiempo de espera hasta poder intentarlo de nuevo; el campo de contraseña queda deshabilitado durante ese tiempo
  ```

---

#### [CA-003] RF-1.5 CA4 — "Múltiples llamadas simultáneas" sin condición verificable
- **CA actual**: "Si múltiples llamadas simultáneas reciben 401, redirigir al login una sola vez"
- **Problema**: "Una sola vez" no es verificable sin especificar el comportamiento observable: ¿se cancela el resto de llamadas? ¿Se muestra algún mensaje?
- **Sugerencia de reformulación**:
  ```
  GIVEN la sesión ha expirado mientras la trabajadora tiene la app abierta con múltiples operaciones en curso
  WHEN el servidor responde con "sesión inválida" a cualquiera de esas operaciones
  THEN se muestra la pantalla de login una única vez, se cancelan las operaciones pendientes y no se muestran múltiples diálogos de error superpuestos
  ```

---

#### [CA-004] RF-2.1 CA2 — "Configurable según estado" sin estados definidos
- **CA actual**: "Home de SAD: priorizar servicio activo + fichaje como acción principal. El contenido es configurable según estado..."
- **Problema**: "Configurable según estado" sin enumerar qué estados existen ni qué muestra la home en cada uno hace el CA no verificable.
- **Sugerencia de reformulación** (pendiente de respuesta a [P-002]):
  ```
  GIVEN la trabajadora SAD abre la home
  WHEN tiene un servicio activo en curso
  THEN la home muestra como elemento principal el servicio activo con el botón de fichar salida; los demás accesos directos aparecen debajo
  ```
  *(requiere CAs separados para cada estado: sin servicios, con servicio próximo, con llamamiento pendiente, etc.)*

---

#### [CA-005] RF-3.2 CA2 — Pendiente de revisión RGPD sin criterio de aceptación definible
- **CA actual**: "Mostrar información del cliente (nombre, dirección, edad). Información de salud: pendiente de revisión RGPD — consultar con legal antes de mostrar medicación u otros datos persistentes de salud"
- **Problema**: El CA no puede escribirse en GIVEN/WHEN/THEN mientras la decisión RGPD esté abierta. Es un gap CRÍTICO funcional.
- **Véase gap [P-003].**

---

#### [CA-006] RF-3.4 CA8 — "Puede computar como rechazo por inacción (pendiente de revisión legal)"
- **CA actual**: "Las llamadas caducan automáticamente tras el tiempo límite configurado desde backoffice; si no hay respuesta puede computar como rechazo por inacción (pendiente de revisión legal)"
- **Problema**: El comportamiento después de caducar sin respuesta no está definido. "Pendiente de revisión legal" es una decisión abierta que impide escribir el CA.
- **Véase gap [P-004].**

---

#### [CA-007] RF-8.2 CA10 — Cómputo de vacaciones no definido
- **CA actual**: "Las vacaciones se computan por días naturales (pendiente de confirmar con cliente/legal)"
- **Problema**: No puede escribirse un CA para el cómputo de vacaciones mientras esta decisión esté abierta.
- **Véase gap [P-005].**

---

#### [CA-008] RF-9.1 CA1 — Tipo de contrato con inconsistencia de datos declarada
- **CA actual**: "Contrato (solo SAD): Tipo (Indefinido, Fijo Discontinuo) ⚠️ El Swagger v1.6.0 devuelve `contract_type: "Tiempo completo" | "Tiempo parcial"` — pendiente alinear con backend si son el mismo campo o dos dimensiones distintas"
- **Problema**: El CA no puede verificarse porque los valores que muestra la pantalla no están definidos.
- **Véase gap [P-006].**

---

#### [CA-009] RF-4.1 CA9 — Mensaje de notificación previa al fichaje con nombres dinámicos
- **CA actual**: "El servidor envía una notificación push N minutos antes del inicio del servicio (N configurable en servidor), momento a partir del cual la trabajadora ya puede fichar. El mensaje de la notificación debe incluir el nombre de la trabajadora y el nombre del receptor del servicio"
- **Problema**: El valor N no está definido y el CA mezcla comportamiento del servidor (envío) con el de la app (recepción). Necesita separarse.
- **Sugerencia de reformulación**:
  ```
  GIVEN la trabajadora tiene un servicio programado
  WHEN faltan N minutos para el inicio del servicio (N configurado en el sistema)
  THEN la trabajadora recibe una notificación push con el mensaje "Buenos días [nombre trabajadora], ya puedes fichar para el servicio del Sr./Sra. [nombre receptor]" y el botón de fichar entrada queda habilitado
  ```

---

## Puntos pendientes de validación con cliente

> Estos puntos **no fueron inferidos por el sistema**. Son ambigüedades o información ausente
> que debe ser definida por el cliente antes de generar el `.spec` final.
> **Instrucción**: escribe la respuesta del cliente en el campo "Respuesta" de cada punto.
>
> - `[CRÍTICO]`: afecta directamente a las HUs indicadas en "Afecta". Si se deja sin responder, esas HUs se marcarán como `[INCOMPLETO]` en el spec — se generarán con la información disponible pero no podrán avanzar a plan/tasks hasta completarse.
> - `[INFORMATIVO]`: si no se responde, se aplicará la "Asunción por defecto" indicada.

---

### [P-001][CRÍTICO] Comportamiento del bloqueo temporal de login tras intentos fallidos

- **Contexto**: RF-1.3 CA4 — "Bloqueo temporal tras N intentos fallidos (N configurable en servidor)"
- **Problema**: El documento no define qué ve el usuario durante el bloqueo ni cómo puede desbloquearse. No está claro si la app simplemente muestra un mensaje con el tiempo de espera, si envía un email de desbloqueo, o si el desbloqueo es solo temporal (esperar X minutos). Sin esto, el CA de bloqueo no puede escribirse.
- **Afecta**: funcionalidad de inicio de sesión (RF-1.3)
- **Pregunta para el cliente**: Cuando una trabajadora queda bloqueada temporalmente por intentos fallidos, ¿qué experimenta exactamente? ¿Solo se muestra un mensaje con el tiempo restante y el campo queda deshabilitado ese tiempo? ¿Puede desbloquear su cuenta por algún mecanismo (email, soporte)? ¿El bloqueo es por dispositivo o por cuenta?
- **Respuesta**: _(pendiente)_

---

### [P-002][CRÍTICO] Estados posibles de la home SAD y contenido de cada estado

- **Contexto**: RF-2.1 CA2 — "El contenido es configurable según estado (servicio activo, próximos servicios, llamamientos pendientes, etc.)"
- **Problema**: El documento enumera ejemplos de estados pero no los define de forma exhaustiva ni especifica qué muestra exactamente la home en cada caso. Sin la enumeración completa de estados y su contenido, no pueden escribirse los CAs de la home SAD.
- **Afecta**: funcionalidad de home del perfil SAD (RF-2.1)
- **Pregunta para el cliente**: ¿Cuáles son todos los estados posibles de la home SAD (p. ej.: sin servicios asignados, con servicio activo en curso, con próximo servicio hoy pero sin empezar, con llamamiento pendiente, con servicio activo + llamamiento pendiente simultáneamente, etc.)? ¿Qué muestra la home en cada uno de esos estados como elemento principal?
- **Respuesta**: _(pendiente)_

---

### [P-003][CRÍTICO] Datos de salud del cliente en el detalle del servicio — decisión RGPD

- **Contexto**: RF-3.2 CA2 — "Información de salud: pendiente de revisión RGPD — consultar con legal antes de mostrar medicación u otros datos persistentes de salud en el lado de la cuidadora"
- **Problema**: El alcance de los datos de salud visibles para la cuidadora es una decisión funcional no resuelta. Si la cuidadora puede ver la medicación del cliente, el spec debe describirlo con sus restricciones; si no puede, debe indicarse como fuera de alcance. Sin esta decisión no puede completarse el CA de detalle del servicio.
- **Afecta**: funcionalidad de detalle del servicio (RF-3.2), en particular la sección de información del cliente
- **Pregunta para el cliente**: Tras la revisión con legal, ¿qué datos de salud del cliente puede ver la cuidadora en el detalle del servicio? ¿Solo se muestran el nombre, dirección y edad, y la medicación/historial clínico queda explícitamente fuera de alcance? ¿O sí hay datos de salud visibles con alguna restricción de visualización?
- **Respuesta**: _(pendiente)_

---

### [P-004][CRÍTICO] Comportamiento del llamamiento caducado sin respuesta de la trabajadora

- **Contexto**: RF-3.4 CA8 — "si no hay respuesta puede computar como rechazo por inacción (pendiente de revisión legal)"
- **Problema**: El comportamiento tras caducidad del llamamiento sin respuesta tiene impacto funcional directo en la trabajadora (afecta a su historial, a posibles consecuencias laborales). Sin la decisión legal/funcional este comportamiento no puede definirse.
- **Afecta**: funcionalidad de llamamientos (RF-3.4), historial de llamamientos (RF-3.5)
- **Pregunta para el cliente**: Cuando un llamamiento caduca sin que la trabajadora haya respondido, ¿qué ocurre desde la perspectiva de la app y del sistema? ¿Se registra como "sin respuesta" (estado neutro), como "rechazo por inacción" (con consecuencias equiparables a rechazar), u otro estado diferenciado? ¿Se notifica a la trabajadora que el llamamiento ha caducado?
- **Respuesta**: _(pendiente)_

---

### [P-005][CRÍTICO] Cómputo de vacaciones: días naturales o días laborables

- **Contexto**: RF-8.2 CA10 — "Las vacaciones se computan por días naturales (pendiente de confirmar con cliente/legal)"
- **Problema**: El método de cómputo de vacaciones afecta directamente a los contadores que ve la trabajadora (saldo disponible, días utilizados). Si el cómputo es incorrecto, los datos mostrados son erróneos. No puede construirse el CA de contadores de vacaciones sin esta definición.
- **Afecta**: funcionalidad de historial de ausencias y contadores de vacaciones (RF-8.2)
- **Pregunta para el cliente**: ¿Las vacaciones se computan por días naturales (incluidos fines de semana y festivos) o por días laborables? ¿Hay tipos de ausencia distintos a vacaciones que también usen este criterio (p. ej. permisos personales, asuntos propios)?
- **Respuesta**: _(pendiente)_

---

### [P-006][CRÍTICO] Tipo de contrato mostrado en perfil y estado del contrato (SAD)

- **Contexto**: RF-9.1 CA1 y RF-9.5 CA1 — "⚠️ El Swagger v1.6.0 devuelve `contract_type: "Tiempo completo" | "Tiempo parcial"` — pendiente alinear con backend si son el mismo campo o dos dimensiones distintas"
- **Problema**: La pantalla de perfil y la sección "Estado del contrato" muestran el tipo de contrato, pero los valores que deben mostrarse no están definidos (el PRD dice "Indefinido / Fijo Discontinuo", la API devuelve "Tiempo completo / Tiempo parcial"). Si son dimensiones distintas, habría que mostrar ambas; si es el mismo campo con nombres diferentes, hay que elegir cuál se muestra al usuario.
- **Afecta**: funcionalidad de ver perfil (RF-9.1), estado del contrato (RF-9.5)
- **Pregunta para el cliente**: En la pantalla de perfil y en "Estado del contrato", ¿qué tipo(s) de contrato debe ver la trabajadora SAD? ¿"Indefinido" / "Fijo Discontinuo" (dimensión jurídica), "Tiempo completo" / "Tiempo parcial" (dimensión de jornada), o ambas dimensiones de forma separada? ¿Se ha alineado ya con el equipo de backend el campo que devuelve la API?
- **Respuesta**: _(pendiente)_

---

### [P-007][CRÍTICO] Flujo de activación de cuenta SAD — contenido y resultado

- **Contexto**: RF-1.2 — "las cuentas se crean desde el backoffice y se envía a la trabajadora un email de activación con un enlace para que establezca sus credenciales"
- **Problema**: El flujo que sigue la trabajadora SAD al activar su cuenta por primera vez desde el enlace de email no está descrito paso a paso. ¿Qué pantalla abre el enlace en la app (o en web)? ¿Qué campos introduce? ¿Qué ocurre al finalizar la activación (entra directamente a la app, vuelve al login)?
- **Afecta**: funcionalidad de activación de cuenta (RF-1.2) del perfil SAD
- **Pregunta para el cliente**: Cuando una trabajadora SAD recibe el email de activación y pulsa el enlace, ¿qué flujo sigue exactamente? ¿El enlace abre la app (si está instalada) o una web? ¿Qué introduce la trabajadora (solo contraseña, o también confirmar email)? ¿Al completar la activación entra directamente al onboarding/home o vuelve a la pantalla de login?
- **Respuesta**: _(pendiente)_

---

### [P-008][CRÍTICO] Textos legales de aceptación y rechazo de llamamientos

- **Contexto**: RF-3.4 CA4 — "el copy de aceptación debe ser claro e inequívoco (solicitar textos oficiales a negocio/legal)" y CA5 — "el copy de rechazo debe ser explícito y distinguirse claramente del de aceptación"
- **Problema**: Los textos del diálogo de firma de aceptación y del diálogo de rechazo tienen validez legal (la trabajadora firma con su dedo). Si estos textos no están definidos, el CA del flujo de firma no puede completarse.
- **Afecta**: funcionalidad de aceptar/rechazar llamamiento (RF-3.4), criterios de firma digital
- **Pregunta para el cliente**: ¿Están ya disponibles los textos legales para el diálogo de aceptación y el diálogo de rechazo de llamamientos? Si no, ¿cuándo estarán disponibles y quién los provee (legal, negocio)?
- **Respuesta**: _(pendiente)_

---

### [P-009][INFORMATIVO] Comportamiento del historial de notificaciones push

- **Contexto**: RF-11.1 — se menciona `GET /api/v1/workers/notifications` para listar historial de notificaciones, pero no se describe la pantalla ni la interacción con las notificaciones del historial.
- **Pregunta para el cliente**: ¿Existe una pantalla de "historial de notificaciones" en la app? Si existe, ¿qué puede hacer la trabajadora desde ahí (solo leer, marcar como leída, borrar)? ¿Las notificaciones del historial también tienen deeplink al contenido relacionado?
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: La app muestra un listado de notificaciones recibidas con título, cuerpo y fecha; tocar una notificación abre el contenido relacionado mediante deeplink; existe la opción de marcar todas como leídas. No se puede borrar notificaciones individuales desde el historial.

---

### [P-010][INFORMATIVO] Comportamiento de la notificación de servicio "próximo mañana" para trabajadoras con múltiples servicios

- **Contexto**: RF-11.1 (tipos de notificación) — "Servicio próximo mañana"
- **Pregunta para el cliente**: Si una trabajadora tiene más de un servicio programado para mañana, ¿recibe una notificación por servicio o una única notificación consolidada ("Tienes X servicios mañana")?
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: Se envía una notificación separada por servicio programado para el día siguiente, cada una con deeplink al detalle del servicio correspondiente.

---

### [P-011][INFORMATIVO] Estado vacío de la lista de ofertas para perfil Hogar

- **Contexto**: RF-6.1 CA10 — "Estado vacío cuando no hay ofertas coincidentes"
- **Pregunta para el cliente**: Cuando no hay ofertas que coincidan con los filtros aplicados, ¿qué mensaje ve la trabajadora? ¿Se diferencia el estado "no hay ofertas con estos filtros" del estado "no hay ofertas en ningún caso"? ¿Hay alguna CTA sugerida (p. ej. "amplía tu zona" o "modifica los filtros")?
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: Se muestra un mensaje genérico "No se han encontrado ofertas con los filtros actuales" con un botón para limpiar filtros. No se diferencia entre filtros activos o ausencia total de ofertas.

---

### [P-012][INFORMATIVO] Comportamiento al intentar borrar una conversación con mensajes no leídos

- **Contexto**: RF-10.2 CA8 — "Opción de borrar conversación (con confirmación)"
- **Pregunta para el cliente**: ¿Puede la trabajadora borrar una conversación que tiene mensajes no leídos? ¿Se muestra alguna advertencia adicional antes de confirmar el borrado en ese caso?
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: La trabajadora puede borrar cualquier conversación con confirmación, independientemente del estado de lectura. El diálogo de confirmación estándar no hace referencia a mensajes no leídos.

---

### [P-013][INFORMATIVO] Comportamiento del porcentaje de completitud de perfil en Hogar — campos que cuentan

- **Contexto**: RF-9.1 CA8 — "Indicador de porcentaje de completitud del perfil visible en la pantalla principal del perfil" y CA12 — "(Solo Hogar) El porcentaje de completitud del perfil debe ser visible desde la home"
- **Pregunta para el cliente**: ¿Qué campos del perfil computan para el porcentaje de completitud? ¿Es el mismo cálculo para Hogar y SAD, o solo aplica a Hogar?
- **Respuesta**: _(pendiente)_
- **Asunción por defecto**: El porcentaje de completitud computa los campos de la sección Información Personal, Profesional e Idiomas. La foto de perfil suma al porcentaje pero es opcional. El cálculo exacto lo provee el backend. El indicador visible en home solo aplica al perfil Hogar.

---

## Próximos pasos

1. En la sección "Pureza", para cada contaminación marca **una** de las tres acciones:
   - `[x] ACEPTAR` — se usará la reescritura tal cual en el spec
   - `[x] EDITAR` — modifica el texto de "Reescritura sugerida" y marca esta opción
   - `[x] RECHAZAR (justificar)` — añade tu justificación; el texto original se conservará como excepción documentada
2. Responder los puntos `[CRÍTICO]` que puedas — los que queden sin respuesta marcarán sus HUs como `[INCOMPLETO]` en el spec (se generarán pero no podrán avanzar a plan/tasks)
3. Responder los puntos `[INFORMATIVO]` si tienes la información — si no, se aplicará la asunción por defecto
4. Una vez revisado, ejecutar:
   ```
   /wf-spec-finalize prd-hogar-sad.md
   ```
5. Para completar HUs marcadas `[INCOMPLETO]` después: responde los gaps pendientes en este archivo y ejecuta `/wf-spec-delta`
