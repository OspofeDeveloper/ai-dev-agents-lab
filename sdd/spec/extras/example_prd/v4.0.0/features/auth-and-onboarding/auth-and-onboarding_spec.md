# Spec: Autenticación y Onboarding
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-001 via prd-hogar-sad_discovery.md)
> Feature ID: F-001
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|-----------------------------|
| Trabajadora Hogar | Profesional de cuidado a domicilio con contrato fijo discontinuo (app CUIDEO) | Registrarse con email y contraseña, iniciar sesión, recuperar contraseña, completar onboarding, cerrar sesión |
| Trabajadora SAD | Profesional del Servicio de Asistencia Social con cuenta creada por backoffice (app Felizvita) | Activar cuenta mediante enlace de email, iniciar sesión, recuperar contraseña, completar onboarding, cerrar sesión, ver pantalla de acceso revocado |

---

## Historias de Usuario

### HU-001: Splash y redirección inicial
Como trabajadora (Hogar o SAD),
quiero que la app muestre una pantalla de bienvenida al abrirse y me lleve automáticamente al lugar correcto,
para que no tenga que navegar manualmente al inicio de cada sesión.

### HU-002: Onboarding en el primer acceso
Como trabajadora (Hogar o SAD) que accede por primera vez,
quiero ver una presentación de las funcionalidades principales de la app,
para que pueda entender qué ofrece y configurar los permisos necesarios antes de empezar a usarla.

### HU-003: Registro de cuenta (Hogar)
Como trabajadora Hogar sin cuenta,
quiero registrarme en la app introduciendo mi email y una contraseña,
para que pueda acceder a las funcionalidades de la aplicación.

### HU-004: Activación de cuenta (SAD)
Como trabajadora SAD cuya cuenta ha sido creada por coordinación,
quiero activar mi cuenta a través de un enlace recibido por email y establecer mi contraseña,
para que pueda acceder a la app con mis credenciales propias.

### HU-005: Inicio de sesión
Como trabajadora (Hogar o SAD) con cuenta activa,
quiero iniciar sesión con mi email y contraseña,
para que pueda acceder a las funcionalidades de la app sin tener que volver a autenticarme en cada visita.

### HU-006: Sesión persistente
Como trabajadora (Hogar o SAD) que ya ha iniciado sesión,
quiero que la app recuerde mi sesión activa entre usos,
para que no tenga que introducir mis credenciales cada vez que abro la aplicación.

### HU-007: Recuperación de contraseña
Como trabajadora (Hogar o SAD) que ha olvidado su contraseña,
quiero poder solicitar un email de recuperación y establecer una nueva contraseña,
para que pueda recuperar el acceso a mi cuenta sin necesidad de contactar con coordinación.

### HU-008: Gestión de la sesión activa
Como trabajadora (Hogar o SAD) con sesión iniciada,
quiero que la app detecte automáticamente cuándo mi sesión ha caducado o ha sido invalidada,
para que sea redirigida al inicio de sesión de forma clara y sin comportamientos inesperados.

### HU-009: Cierre de sesión
Como trabajadora (Hogar o SAD),
quiero poder cerrar sesión explícitamente,
para que mis datos queden protegidos si comparto el dispositivo o cambio de cuenta.

### HU-010: Acceso revocado (SAD)
Como trabajadora SAD cuya cuenta ha sido suspendida o dada de baja,
quiero ver una pantalla informativa cuando intento acceder,
para que entienda que ya no tengo acceso y sepa cómo contactar con coordinación si es un error.

---

## Recorridos de Usuario

### Journey 1: Primera apertura — registro Hogar
Actor: Trabajadora Hogar | Objetivo: Crear cuenta y completar onboarding

1. La trabajadora abre la app por primera vez.
2. La app muestra la pantalla de splash con el logo durante 2-3 segundos.
3. Al no detectar sesión activa, la app redirige a la pantalla de inicio de sesión.
4. La trabajadora pulsa el enlace de registro.
5. La trabajadora introduce su email y elige una contraseña que cumpla los requisitos de seguridad.
6. La app valida los campos y registra la cuenta; la trabajadora queda autenticada.
7. La app solicita el permiso de notificaciones push (antes del onboarding).
8. La app muestra el onboarding (3-5 pantallas) explicando las funcionalidades principales.
9. Durante el onboarding, la app solicita el permiso de ubicación con explicación de su uso.
10. La trabajadora completa el onboarding y la app redirige al panel principal.

Estado de éxito: La trabajadora Hogar tiene cuenta activa y ha completado el onboarding. El estado de onboarding queda registrado localmente para no volver a mostrarse.

Flujos alternativos:
- Si el email introducido ya está registrado → la app muestra un error indicando que el email ya existe.
- Si la contraseña no cumple los requisitos → la app muestra los requisitos incumplidos sin enviar el formulario.
- Si la trabajadora rechaza el permiso de notificaciones → continúa al onboarding sin registrar notificaciones.
- Si la trabajadora rechaza el permiso de ubicación → continúa al panel principal; podrá ser solicitado de nuevo cuando use el fichaje.

---

### Journey 2: Primera apertura — activación SAD
Actor: Trabajadora SAD | Objetivo: Activar cuenta y completar onboarding

1. La trabajadora recibe un email de activación enviado por coordinación.
2. La trabajadora pulsa el enlace del email; la app se abre (o el navegador muestra el flujo de activación).
3. La trabajadora establece su contraseña cumpliendo los requisitos mínimos de seguridad.
4. La app autentica a la trabajadora con las nuevas credenciales.
5. La app solicita el permiso de notificaciones push.
6. La app muestra el onboarding (3-5 pantallas).
7. Durante el onboarding, la app solicita el permiso de ubicación.
8. La trabajadora completa el onboarding y la app redirige al panel principal.

Estado de éxito: La trabajadora SAD tiene cuenta activa con contraseña propia y ha completado el onboarding.

Flujos alternativos:
- Si el enlace de activación ha caducado → la app muestra un mensaje informativo indicando que el enlace ha caducado y que debe contactar con coordinación para obtener uno nuevo.

---

### Journey 3: Apertura con sesión activa
Actor: Trabajadora (Hogar o SAD) | Objetivo: Acceder a la app sin volver a autenticarse

1. La trabajadora abre la app.
2. La app muestra el splash durante 2-3 segundos.
3. La app verifica en segundo plano que la sesión almacenada sigue activa.
4. Al confirmarse la sesión, la app redirige directamente al panel principal sin mostrar la pantalla de login.

Estado de éxito: La trabajadora accede al panel principal sin ninguna interacción de autenticación.

---

### Journey 4: Sesión caducada o invalidada
Actor: Trabajadora (Hogar o SAD) | Objetivo: Ser informada de que necesita volver a iniciar sesión

1. La trabajadora abre la app (o ya está usándola).
2. La app detecta que la sesión ha caducado o ha sido invalidada por el servidor.
3. La app borra la sesión almacenada localmente.
4. La app redirige a la pantalla de inicio de sesión con un mensaje indicando que la sesión ha expirado.
5. La trabajadora introduce sus credenciales y vuelve a iniciar sesión.

Estado de éxito: La trabajadora es redirigida al login de forma limpia, sin datos residuales de la sesión anterior.

Flujos alternativos:
- Si varias partes de la app detectan simultáneamente la sesión inválida → la redirección al login ocurre una sola vez.

---

### Journey 5: Acceso con cuenta revocada (SAD)
Actor: Trabajadora SAD | Objetivo: Entender que su acceso ha sido suspendido

1. La trabajadora intenta iniciar sesión o abre la app con sesión activa revocada.
2. El servidor responde indicando que la cuenta está suspendida o dada de baja.
3. La app muestra la pantalla de acceso revocado con un mensaje claro.
4. La trabajadora ve información de contacto para resolver la situación con coordinación.
5. La trabajadora no puede navegar a ninguna sección de la app.

Estado de éxito: La trabajadora entiende su situación y tiene información para contactar con coordinación. No hay sesión ni datos almacenados localmente.

---

### Journey 6: Recuperación de contraseña
Actor: Trabajadora (Hogar o SAD) | Objetivo: Recuperar el acceso a su cuenta

1. Desde la pantalla de inicio de sesión, la trabajadora pulsa el enlace de recuperación de contraseña.
2. La app muestra un campo para introducir el email de la cuenta.
3. La trabajadora introduce su email y envía la solicitud.
4. La app muestra un mensaje de confirmación de envío (sin indicar si el email existe en el sistema).
5. La trabajadora recibe un email con un enlace de restablecimiento de contraseña.
6. La trabajadora pulsa el enlace y establece una nueva contraseña que cumpla los requisitos mínimos.
7. La app confirma el cambio y redirige a la pantalla de inicio de sesión.

Estado de éxito: La trabajadora puede iniciar sesión con su nueva contraseña.

Flujos alternativos:
- Si el enlace ha caducado → la app informa de que el enlace ha expirado y permite solicitar uno nuevo.
- Si la cuenta está suspendida → tras seguir el enlace, la app muestra la pantalla de acceso revocado.

---

### Journey 7: Cierre de sesión
Actor: Trabajadora (Hogar o SAD) | Objetivo: Salir de la app de forma segura

1. Desde el menú o el perfil, la trabajadora pulsa la opción de cerrar sesión.
2. La app muestra un diálogo de confirmación con opciones "Cancelar" y "Cerrar sesión".
3. La trabajadora confirma el cierre de sesión.
4. La app elimina todos los datos de sesión locales y notifica al servidor para invalidar el token.
5. La app redirige a la pantalla de inicio de sesión.

Estado de éxito: La sesión queda invalidada tanto localmente como en el servidor. La pantalla de login se muestra limpia.

---

## Resultados y Éxito

- La trabajadora puede acceder a la app de forma segura y fluida, sin repetir la autenticación en cada uso mientras su sesión sea válida.
- El onboarding se muestra exactamente una vez (en el primer acceso exitoso) y presenta las funcionalidades principales de forma comprensible para ambos perfiles.
- Los permisos del dispositivo (notificaciones, ubicación) se solicitan en el momento adecuado del flujo, con explicación de su uso.
- Las sesiones inactivas, caducadas o revocadas son detectadas y resueltas automáticamente, redirigiendo a la trabajadora al inicio de sesión sin pérdida de datos.
- Las trabajadoras SAD con cuenta revocada ven una pantalla informativa y no pueden acceder a la app.
- El cierre de sesión garantiza que no quedan datos de sesión en el dispositivo ni en el servidor.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Splash:**
- El splash se muestra siempre al arrancar la app, independientemente del estado de sesión.
- Duración fija: 2 segundos mínimo, 3 segundos máximo. No se salta con interacción del usuario.
- Tras el splash: si hay sesión válida → panel principal; si no hay sesión o es inválida → pantalla de login.

**Registro (solo Hogar):**
- Requisitos de contraseña: mínimo 8 caracteres, al menos una mayúscula y al menos un número.
- El email se valida en formato antes de enviar el formulario.
- Si el email ya existe en el sistema, la app muestra un error específico: "Este email ya está registrado. ¿Quieres iniciar sesión?"
- Tras el registro exitoso, la trabajadora queda autenticada directamente sin un paso de verificación de email.

**Activación (solo SAD):**
- Las cuentas SAD no se pueden crear desde la app; solo mediante enlace de activación enviado por coordinación.
- El enlace de activación tiene caducidad definida por el servidor. Si ha caducado, se muestra el mensaje: "Este enlace ha caducado. Contacta con tu coordinadora para recibir uno nuevo."
- Al completar la activación, la trabajadora queda autenticada directamente.

**Inicio de sesión:**
- Los campos de email y contraseña se validan antes del envío.
- Tras N intentos fallidos consecutivos (N definido por el servidor), la app muestra el mensaje "Has superado el número de intentos. Inténtalo de nuevo más tarde." y deshabilita el botón de envío hasta que el servidor levante el bloqueo.
- El inicio de sesión automático (sesión persistente) no muestra la pantalla de login; redirige directamente al panel principal.

**Onboarding:**
- El flujo de onboarding se ejecuta siempre después del primer inicio de sesión exitoso (ya sea registro Hogar o activación SAD).
- El orden del flujo inicial es: autenticación → solicitar permiso de notificaciones push → onboarding (3-5 pantallas) → panel principal.
- Durante el onboarding se solicita el permiso de ubicación, explicando que es necesario para el registro de entrada y salida de servicios.
- El permiso de cámara/archivos NO se solicita en el onboarding; se solicita en el momento en que se necesita (por ejemplo, al subir un documento).
- El contenido del onboarding es idéntico para trabajadoras Hogar y SAD.
- El estado de "onboarding completado" se almacena en el dispositivo. Si se reinstala la app o se cambia de dispositivo, el onboarding puede volver a mostrarse.

**Gestión de sesión:**
- La app verifica la validez de la sesión al arrancar. Si la sesión es inválida (caducada o revocada), redirige al login.
- Cualquier respuesta del servidor que indique sesión inválida desencadena el cierre de sesión local y la redirección al login, independientemente de la pantalla en la que esté la trabajadora.
- Si múltiples operaciones simultáneas reciben respuesta de sesión inválida, la redirección al login ocurre una única vez.

**Acceso revocado (solo SAD):**
- Se detecta en la respuesta del servidor al intentar iniciar sesión o al verificar la sesión al arrancar.
- La pantalla de acceso revocado muestra el mensaje: "Ya no tienes permisos para acceder a esta aplicación." e información de contacto con coordinación.
- Desde la pantalla de acceso revocado no hay navegación posible a ninguna sección de la app.
- No se almacenan tokens ni datos de sesión en este estado.

**Recuperación de contraseña:**
- La solicitud de email de recuperación siempre muestra el mismo mensaje de confirmación, independientemente de si el email existe en el sistema (para no revelar información).
- La nueva contraseña debe cumplir los mismos requisitos que el registro: mínimo 8 caracteres, al menos una mayúscula y al menos un número.
- El enlace de recuperación tiene caducidad de 60 minutos.

**Cierre de sesión:**
- El cierre de sesión requiere confirmación explícita mediante diálogo.
- Al cerrar sesión: se eliminan todos los datos de sesión del dispositivo y se notifica al servidor para invalidar el token activo.
- El cierre de sesión elimina el registro del dispositivo para notificaciones push (el dispositivo deja de recibir notificaciones de esa cuenta).

### Destinos de navegación

| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Splash | Sesión válida detectada | Panel principal |
| Splash | Sin sesión o sesión inválida | Pantalla de inicio de sesión |
| Splash | Cuenta revocada (SAD) | Pantalla de acceso revocado |
| Pantalla de login | Credenciales correctas + primer acceso | Solicitud de permiso de notificaciones → Onboarding |
| Pantalla de login | Credenciales correctas + acceso posterior | Panel principal |
| Pantalla de login | Enlace "¿Olvidaste tu contraseña?" | Pantalla de recuperación de contraseña |
| Pantalla de login | Enlace de registro (solo Hogar) | Formulario de registro |
| Formulario de registro | Registro exitoso | Solicitud de permiso de notificaciones → Onboarding |
| Activación por enlace | Activación exitosa | Solicitud de permiso de notificaciones → Onboarding |
| Activación por enlace | Enlace caducado | Mensaje informativo de enlace caducado (sin acceso a la app) |
| Onboarding | Completado | Panel principal |
| Cualquier pantalla autenticada | Sesión inválida detectada | Pantalla de inicio de sesión (una sola redirección) |
| Pantalla de inicio de sesión | Credenciales válidas pero cuenta revocada | Pantalla de acceso revocado |
| Pantalla de recuperación | Email enviado | Mensaje de confirmación de envío |
| Enlace de recuperación | Contraseña restablecida | Pantalla de inicio de sesión |
| Enlace de recuperación | Enlace caducado | Mensaje de enlace caducado + opción de solicitar nuevo enlace |
| Enlace de recuperación | Cuenta suspendida | Pantalla de acceso revocado |
| Opción "Cerrar sesión" | Confirmación del diálogo | Pantalla de inicio de sesión |

---

## Criterios de Aceptación

### CA-001: Splash muestra logo y redirige según estado de sesión ← HU-001
GIVEN la trabajadora abre la aplicación
WHEN la app arranca
THEN se muestra la pantalla de splash con el logo de la app durante 2-3 segundos y, a continuación, redirige automáticamente al panel principal si hay sesión válida, o a la pantalla de login si no hay sesión o ésta es inválida

### CA-002: Splash detecta cuenta revocada ← HU-001
GIVEN la trabajadora SAD abre la app y su cuenta ha sido revocada
WHEN la app verifica el estado de la sesión al arrancar
THEN la app redirige a la pantalla de acceso revocado en lugar del panel principal o el login

### CA-003: Onboarding se muestra solo en el primer acceso ← HU-002
GIVEN la trabajadora (Hogar o SAD) ha completado el proceso de autenticación por primera vez
WHEN la app detecta que el onboarding no ha sido completado en este dispositivo
THEN la app solicita primero el permiso de notificaciones push y luego muestra el onboarding de 3-5 pantallas antes de redirigir al panel principal

### CA-004: Onboarding no se repite en accesos posteriores ← HU-002
GIVEN la trabajadora ya completó el onboarding en este dispositivo
WHEN la trabajadora inicia sesión en un acceso posterior
THEN la app redirige directamente al panel principal sin mostrar el onboarding

### CA-005: Permiso de ubicación solicitado durante onboarding ← HU-002
GIVEN la trabajadora está completando el onboarding
WHEN la app muestra las pantallas de bienvenida
THEN la app solicita el permiso de ubicación mostrando una explicación de que es necesario para el registro de entrada y salida de servicios

### CA-006: Permiso de cámara no se solicita en el onboarding ← HU-002
GIVEN la trabajadora está completando el onboarding
WHEN la app muestra las pantallas de bienvenida
THEN la app NO solicita el permiso de cámara ni archivos en ningún momento del onboarding

### CA-007: Registro Hogar con email y contraseña ← HU-003
GIVEN la trabajadora Hogar pulsa el enlace de registro
WHEN introduce un email válido y una contraseña que cumpla los requisitos (mínimo 8 caracteres, una mayúscula, un número)
THEN la app registra la cuenta, autentica a la trabajadora y continúa al flujo de onboarding

### CA-008: Validación de contraseña en registro ← HU-003
GIVEN la trabajadora Hogar está en el formulario de registro
WHEN introduce una contraseña que no cumple los requisitos mínimos de seguridad
THEN la app muestra los requisitos incumplidos específicos y no permite enviar el formulario

### CA-009: Email duplicado en registro ← HU-003
GIVEN la trabajadora Hogar introduce un email que ya está registrado en el sistema
WHEN envía el formulario de registro
THEN la app muestra el mensaje: "Este email ya está registrado. ¿Quieres iniciar sesión?" y no crea una cuenta nueva

### CA-010: Activación de cuenta SAD mediante enlace ← HU-004
GIVEN la trabajadora SAD recibe un email de activación y pulsa el enlace
WHEN el enlace es válido y no ha caducado
THEN la app muestra un formulario para establecer la contraseña, y tras completarlo, autentica a la trabajadora y continúa al flujo de onboarding

### CA-011: Enlace de activación caducado ← HU-004
GIVEN la trabajadora SAD pulsa un enlace de activación caducado
WHEN la app procesa el enlace
THEN la app muestra el mensaje: "Este enlace ha caducado. Contacta con tu coordinadora para recibir uno nuevo." sin dar acceso a la app

### CA-012: Inicio de sesión con credenciales correctas ← HU-005
GIVEN la trabajadora (Hogar o SAD) tiene cuenta activa y ha completado el onboarding
WHEN introduce su email y contraseña correctos y pulsa iniciar sesión
THEN la app autentica a la trabajadora y redirige al panel principal

### CA-013: Inicio de sesión con credenciales incorrectas ← HU-005
GIVEN la trabajadora (Hogar o SAD) está en la pantalla de inicio de sesión
WHEN introduce email o contraseña incorrectos
THEN la app muestra un mensaje de error claro indicando que las credenciales no son correctas

### CA-014: Bloqueo temporal por intentos fallidos ← HU-005
GIVEN la trabajadora ha superado el número máximo de intentos de inicio de sesión fallidos (N definido por el servidor)
WHEN intenta volver a iniciar sesión
THEN la app muestra el mensaje "Has superado el número de intentos. Inténtalo de nuevo más tarde." y el botón de inicio de sesión queda deshabilitado hasta que el servidor levante el bloqueo

### CA-015: Sesión persistente entre aperturas ← HU-006
GIVEN la trabajadora (Hogar o SAD) tiene una sesión activa válida en el dispositivo
WHEN abre la app en un acceso posterior
THEN la app redirige directamente al panel principal sin mostrar la pantalla de inicio de sesión

### CA-016: Solicitud de recuperación de contraseña ← HU-007
GIVEN la trabajadora (Hogar o SAD) pulsa el enlace de recuperación en la pantalla de login
WHEN introduce su email y envía la solicitud
THEN la app muestra un mensaje de confirmación de envío genérico, sin revelar si el email existe en el sistema

### CA-017: Restablecimiento de contraseña mediante enlace ← HU-007
GIVEN la trabajadora recibe y pulsa el enlace de recuperación (válido, no caducado)
WHEN introduce y confirma una nueva contraseña que cumple los requisitos mínimos
THEN la app actualiza la contraseña y redirige a la pantalla de inicio de sesión

### CA-018: Enlace de recuperación caducado ← HU-007
GIVEN la trabajadora pulsa un enlace de recuperación de contraseña que ha caducado (más de 60 minutos)
WHEN la app procesa el enlace
THEN la app informa de que el enlace ha expirado y ofrece la opción de solicitar un nuevo email de recuperación

### CA-019: Detección de sesión inválida durante el uso ← HU-008
GIVEN la trabajadora (Hogar o SAD) está usando la app con una sesión que ha sido invalidada por el servidor
WHEN la app recibe una respuesta del servidor indicando sesión inválida
THEN la app cierra la sesión local, elimina los datos de sesión almacenados y redirige a la pantalla de inicio de sesión mostrando el mensaje "Tu sesión ha expirado. Vuelve a iniciar sesión."

### CA-020: Redirección única ante invalidación simultánea ← HU-008
GIVEN múltiples operaciones en la app reciben simultáneamente una respuesta de sesión inválida
WHEN todas ellas se procesan
THEN la redirección al inicio de sesión ocurre una sola vez, sin pantallas superpuestas ni bucles de navegación

### CA-021: Diálogo de confirmación de cierre de sesión ← HU-009
GIVEN la trabajadora (Hogar o SAD) pulsa la opción de cerrar sesión
WHEN la opción es seleccionada
THEN la app muestra un diálogo con las opciones "Cancelar" y "Cerrar sesión" antes de proceder

### CA-022: Cierre de sesión elimina datos locales y notifica al servidor ← HU-009
GIVEN la trabajadora confirma el cierre de sesión en el diálogo
WHEN se ejecuta el cierre de sesión
THEN la app elimina todos los datos de sesión del dispositivo, notifica al servidor para invalidar el token activo y redirige a la pantalla de inicio de sesión

### CA-023: Pantalla de acceso revocado (SAD) ← HU-010
GIVEN la trabajadora SAD intenta iniciar sesión o la app detecta la cuenta revocada al arrancar
WHEN el servidor responde indicando cuenta suspendida, dada de baja o desactivada
THEN la app muestra la pantalla de acceso revocado con el mensaje: "Ya no tienes permisos para acceder a esta aplicación." e información de contacto para resolver la situación

### CA-024: Sin navegación desde pantalla de acceso revocado ← HU-010
GIVEN la trabajadora SAD está en la pantalla de acceso revocado
WHEN intenta navegar a cualquier sección de la app
THEN no hay ningún acceso posible a funcionalidades de la app; la pantalla de acceso revocado es la única vista disponible

### CA-025: No se almacenan datos de sesión con cuenta revocada ← HU-010
GIVEN la trabajadora SAD ve la pantalla de acceso revocado
WHEN la pantalla se muestra
THEN no se almacena ningún token ni datos de sesión en el dispositivo

---

## Checklist de Validación

- [x] Actores identificados (Trabajadora Hogar y Trabajadora SAD con capacidades diferenciadas)
- [x] Flujos principales descritos paso a paso (7 journeys: splash, registro Hogar, activación SAD, sesión persistente, sesión caducada, acceso revocado, recuperación contraseña, cierre de sesión)
- [x] Estados de éxito definidos para cada journey
- [x] Edge cases documentados (email duplicado, contraseña débil, enlace caducado, bloqueo por intentos, múltiples respuestas de sesión inválida simultáneas)
- [x] Estados de error definidos (credenciales incorrectas, bloqueo temporal, enlace caducado, cuenta revocada)
- [x] Ambigüedades resueltas (ver Asunciones Aplicadas)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes (tabla completa en Instrucciones Inambiguas)

---

## Fuera de Alcance

- **Autenticación biométrica** (Face ID, huella digital): no forma parte de este spec ni del MVP.
- **Autenticación de dos factores (2FA)**: fuera del alcance del MVP.
- **Gestión de notificaciones push**: la solicitud de permiso de notificaciones durante el onboarding está incluida en este spec, pero la lógica completa de registro de dispositivo, entrega de notificaciones y deeplinks forma parte de F-009 (push-notifications).
- **Registro de dispositivo para notificaciones**: la baja del dispositivo al cerrar sesión es un efecto de esta feature, pero la lógica de gestión de tokens de notificaciones pertenece a F-009 (push-notifications).
- **Perfil de la trabajadora**: la creación de la entidad Worker durante el registro pertenece a este spec; la gestión completa del perfil (edición, documentos, firma digital) forma parte de F-008 (profile-management).
- **Panel principal**: el destino final tras el onboarding pertenece a F-002 (home-dashboard).
- **Activación y gestión de cuentas desde backoffice**: la creación y revocación de cuentas SAD es responsabilidad del sistema de backoffice y no forma parte de la app móvil.

---

## Asunciones Aplicadas

- **[A-001]**: El onboarding se solicita siempre en el dispositivo donde se completa el primer acceso. Si la trabajadora reinstala la app o cambia de dispositivo, el estado de onboarding completado puede no estar disponible y el onboarding puede volver a mostrarse. Esta asunción es conservadora: prioriza garantizar que todas las trabajadoras ven el onboarding sobre evitar una repetición ocasional.

- **[A-002]**: Cuando la app detecta que la sesión ha sido revocada, el bloqueo temporal por intentos fallidos de inicio de sesión (CA-014), la duración exacta del bloqueo y el número N de intentos son configurados por el servidor. La app muestra el mensaje de bloqueo y deshabilita el botón de envío; no implementa un temporizador propio de cuenta atrás.

- **[A-003]**: El permiso de ubicación solicitado durante el onboarding (CA-005) se solicita aunque el perfil de la trabajadora sea Hogar. El PRD especifica que el onboarding es idéntico para ambos perfiles. Aunque el fichaje geolocalizado es exclusivo de SAD, la solicitud de ubicación se incluye en el onboarding compartido tal como indica el PRD.
