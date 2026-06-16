# Patrones de Error en PRDs

Estos son los errores más frecuentes al escribir un PRD para el pipeline SDD. Para cada patrón se incluye el problema, la señal de detección y la reescritura correcta.

---

## Error 1: Objetivo de negocio disfrazado de feature

**Problema:** El PRD lista metas estratégicas como si fueran funcionalidades entregables. El pipeline no puede generar un Spec de algo que no es una capacidad de usuario.

**Señal:** La frase no describe qué puede hacer un actor — describe un resultado que el negocio quiere lograr.

| Incorrecto (objetivo de negocio) | Correcto (capacidad de usuario) |
|---|---|
| "Mejorar la retención de cuidadoras" | "La cuidadora puede ver su historial de servicios completados" |
| "Aumentar la eficiencia operativa" | "El coordinador puede asignar múltiples servicios desde una sola pantalla" |
| "Digitalizar el proceso de onboarding" | "La trabajadora puede completar su registro y subir documentación desde la app" |

---

## Error 2: Tarea técnica disfrazada de feature

**Problema:** El PRD describe trabajo de ingeniería, no capacidades de usuario. El pipeline intentará generar un Spec de algo que en realidad es una tarea del Plan o de Tasks.

**Señal:** La frase tiene como sujeto "el sistema", "la app" o un componente técnico — no un actor de negocio.

| Incorrecto (tarea técnica) | Correcto (capacidad de usuario) |
|---|---|
| "Integrar Firebase para notificaciones push" | "El usuario recibe notificaciones cuando hay novedades en sus servicios" |
| "Implementar refresh token automático" | "El usuario permanece autenticado sin necesidad de volver a hacer login" |
| "Crear módulo de geolocalización" | "El sistema valida que el cuidador está en la ubicación del servicio al fichar" |
| "Sincronización de datos offline" | "El cuidador puede consultar sus servicios del día sin conexión a internet" |

---

## Error 3: Pantalla como feature

**Problema:** El PRD organiza el alcance por pantallas en lugar de por capacidades de usuario. Una pantalla puede contener varias capacidades, y una capacidad puede abarcar varias pantallas — son conceptos distintos.

**Señal:** Los ítems del alcance son nombres de pantallas o vistas ("Pantalla de login", "Vista de detalle", "Tab de servicios").

| Incorrecto (pantalla) | Correcto (capacidad) |
|---|---|
| "Pantalla de login" | "El usuario puede autenticarse con email y contraseña" |
| "Pantalla de servicios" | "La cuidadora puede ver sus servicios asignados para la semana" |
| "Modal de confirmación de fichaje" | "El sistema solicita confirmación antes de registrar la entrada/salida" |

---

## Error 4: Actor implícito o ambiguo

**Problema:** Las capacidades se describen sin especificar qué actor las tiene. Cuando hay múltiples perfiles, el pipeline no puede asignar la feature al actor correcto.

**Señal:** Frases con "el usuario puede..." sin definir qué tipo de usuario, o capacidades que aparecen en secciones sin cabecera de actor.

| Incorrecto (actor ambiguo) | Correcto (actor explícito) |
|---|---|
| "Los usuarios pueden ver el historial" | "La cuidadora puede ver su historial de servicios completados" |
| "Se puede gestionar la disponibilidad" | "La cuidadora puede marcar sus zonas de disponibilidad por semana" |
| "Permite adjuntar documentos" | "La trabajadora puede adjuntar documentos a su perfil (PDF, JPG, PNG)" |

**Importante:** este error no significa que el PRD tenga que organizarse obligatoriamente por actor. Significa que, aunque esté organizado por RFs o por áreas funcionales, el actor de cada capacidad debe quedar explícito.

---

## Error 5: Scope mezclado — MVP con fases futuras sin separación clara

**Problema:** Las funcionalidades de la versión actual y las de fases futuras se describen en el mismo nivel, sin separación explícita. El pipeline genera specs para todo lo que aparece en el alcance.

**Señal:** Frases como "en una fase posterior", "se podría añadir", "no para el MVP" aparecen dentro de la sección de alcance en lugar de en la sección de fuera-de-alcance.

**Correcto:** Todo lo que no es MVP va en la sección `## Fuera del Alcance` con el motivo "fase futura", no mezclado con el scope actual.

---

## Error 6: Contaminación técnica en reglas de negocio

**Problema:** Las restricciones de negocio se expresan como restricciones técnicas. El pipeline las trata como requisitos funcionales pero el Spec resultante queda contaminado.

| Incorrecto (técnico) | Correcto (negocio) |
|---|---|
| "Los adjuntos deben ser MIME type image/jpeg o application/pdf" | "Los adjuntos deben ser imágenes (JPG, PNG) o documentos (PDF)" |
| "El token de sesión expira a las 24 horas" | "La sesión permanece activa durante 24 horas sin actividad" |
| "Las coordenadas GPS se validan con un radio de 200 metros" | "El sistema considera válido el fichaje si el cuidador está en las proximidades del domicilio del cliente" |
| "Las notificaciones usan FCM/APNs" | "El usuario recibe notificaciones en su dispositivo aunque la app esté cerrada" |

---

## Error 7: Fuera-de-alcance vacío o genérico

**Problema:** La sección de fuera-de-alcance no existe o dice algo como "todo lo no mencionado". Sin exclusiones explícitas, el implementador asumirá que las funcionalidades relacionadas están incluidas.

**Señal:** Sección ausente, o con frases vagas que no nombran funcionalidades específicas.

| Incorrecto | Correcto |
|---|---|
| "Funcionalidades no descritas en este documento" | "Gestión de nóminas: gestionada por el back-office, fuera de la app" |
| "Cualquier feature no incluida en el alcance" | "Videollamadas con coordinadores: fase futura, no incluida en el MVP" |
| (sección ausente) | "Administración de usuarios y roles: responsabilidad del back-office, sin interfaz en la app" |

---

## Error 8: PRD en nivel de Spec

**Problema:** El PRD ya incluye flujos paso a paso, criterios de aceptación implícitos o decisiones funcionales muy granulares. No es incorrecto — el pipeline lo procesa — pero genera trabajo duplicado y reduce la calidad del análisis de gaps.

**Señal:** El PRD describe "el usuario pulsa X, aparece Y, si Z entonces W".

**Recomendación:** Si el PRD tiene este nivel de detalle, no hay que eliminarlo — pero sí revisar que no incluya decisiones técnicas camufladas como decisiones funcionales. El `wf-spec-analyze` generará menos preguntas de las que generaría con un PRD de más alto nivel, lo que puede dejar gaps sin detectar.

---

## Cómo usar este archivo

Al revisar un PRD, recorre cada patrón y busca coincidencias en el texto. Para cada error encontrado:
1. Cita el fragmento exacto del PRD
2. Identifica el patrón (Error 1–8)
3. Propón la reescritura correcta

Si el error es técnico (Errores 2, 6), indica además en qué capa del pipeline pertenece el contenido (Plan o Tasks).
