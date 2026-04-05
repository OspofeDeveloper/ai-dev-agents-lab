# Spec: Autenticacion y Onboarding
> Version: 1.0 | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md
> Feature ID: F-001

---

## Actores
| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo | Registrarse con email y contrasena, iniciar sesion, recuperar acceso, cerrar sesion |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social | Activar cuenta via email, iniciar sesion, recuperar acceso, cerrar sesion, ver pantalla de acceso revocado |

---

## Historias de Usuario

### HU-001: Splash de bienvenida
Como trabajadora (Hogar o SAD)
quiero ver una pantalla de bienvenida al abrir la app
para que sepa que la aplicacion esta cargando y reconozca la marca.

### HU-002: Onboarding de la app
Como trabajadora (Hogar o SAD)
quiero ver una guia de las funcionalidades principales tras mi primer login
para que entienda que puedo hacer con la aplicacion.

### HU-003: Registro en la app (Hogar)
Como trabajadora Hogar
quiero registrarme con mi email y contrasena
para que pueda acceder a las ofertas de trabajo y gestionar mi perfil.

### HU-004: Activacion de cuenta (SAD)
Como trabajadora SAD
quiero activar mi cuenta mediante el enlace de email enviado por el backoffice
para que pueda establecer mis credenciales y acceder a la aplicacion.

### HU-005: Inicio de sesion
Como trabajadora (Hogar o SAD)
quiero iniciar sesion con mi email y contrasena
para que pueda acceder a las funcionalidades de la app.

### HU-006: Recuperacion de acceso
Como trabajadora (Hogar o SAD)
quiero recuperar mi contrasena si la olvido
para que pueda volver a acceder a mi cuenta.

### HU-007: Gestion del token de sesion
Como trabajadora (Hogar o SAD)
quiero que mi sesion se mantenga activa sin tener que iniciar sesion cada vez
para que el acceso a la app sea rapido y sin friccion.

### HU-008: Cierre de sesion
Como trabajadora (Hogar o SAD)
quiero cerrar mi sesion
para que mis datos queden protegidos cuando no use la app.

### HU-009: Pantalla de acceso revocado (SAD)
Como trabajadora SAD cuya cuenta ha sido suspendida o dada de baja
quiero ver una pantalla informativa que me explique la situacion
para que sepa por que no puedo acceder y como contactar soporte.

---

## Recorridos de Usuario

### Journey 1: Primer acceso — Hogar
Actor: Trabajadora Hogar | Objetivo: Registrarse y acceder a la app por primera vez
1. La trabajadora abre la app y ve la pantalla de splash con el logo de CUIDEO durante 2-3 segundos.
2. La app detecta que no hay sesion activa y muestra la pantalla de login.
3. La trabajadora pulsa "Registrarse" y accede al formulario de registro.
4. La trabajadora introduce su email y elige una contrasena (minimo 8 caracteres, al menos una mayuscula y un numero).
5. La trabajadora envia el formulario y la app inicia sesion automaticamente.
6. La app solicita permiso de notificaciones push.
7. La app muestra 3-5 pantallas de onboarding con los highlights principales.
8. La trabajadora completa el onboarding y accede a la pantalla principal.

Estado de exito: La trabajadora tiene cuenta creada, sesion activa, permisos de notificaciones configurados y ha visto el onboarding.
Flujos alternativos:
- Si el email ya esta registrado: se muestra mensaje de error claro.
- Si la contrasena no cumple requisitos: se muestra error de validacion en linea.

### Journey 2: Primer acceso — SAD
Actor: Trabajadora SAD | Objetivo: Activar su cuenta y acceder por primera vez
1. La trabajadora recibe un email de activacion enviado por el backoffice.
2. La trabajadora accede al enlace del email y establece su contrasena.
3. La trabajadora abre la app y ve la pantalla de splash con el logo de Felizvita.
4. La trabajadora introduce su email y contrasena en la pantalla de login.
5. La app solicita permiso de notificaciones push.
6. La app muestra las pantallas de onboarding.
7. La trabajadora completa el onboarding y accede a la pantalla principal.

Estado de exito: La trabajadora tiene credenciales establecidas, sesion activa y ha visto el onboarding.
Flujos alternativos:
- Si el enlace de activacion ha caducado: la trabajadora debe solicitar un nuevo enlace al backoffice.

### Journey 3: Login habitual
Actor: Trabajadora (Hogar o SAD) | Objetivo: Acceder a la app con sesion previa
1. La trabajadora abre la app y ve la pantalla de splash.
2. La app verifica la validez del token de sesion almacenado.
3. Si el token es valido, la app muestra directamente la pantalla principal sin pedir login.
4. Si el token ha expirado o sido revocado, la app muestra la pantalla de login.

Estado de exito: La trabajadora accede a la pantalla principal sin friccion si su sesion es valida.
Flujos alternativos:
- Si la cuenta esta suspendida o dada de baja: se muestra la pantalla de acceso revocado (Journey 6).

### Journey 4: Recuperacion de contrasena
Actor: Trabajadora (Hogar o SAD) | Objetivo: Recuperar acceso a su cuenta
1. La trabajadora pulsa "Olvidaste tu contrasena?" en la pantalla de login.
2. La app muestra la pantalla de recuperacion con campo de email.
3. La trabajadora introduce su email y pulsa enviar.
4. La app muestra confirmacion de envio (sin revelar si el email existe en el sistema).
5. La trabajadora recibe un email con enlace de restablecimiento.
6. La trabajadora accede al enlace y establece una nueva contrasena.
7. La trabajadora vuelve a la app e inicia sesion con la nueva contrasena.

Estado de exito: La trabajadora puede acceder con su nueva contrasena.
Flujos alternativos:
- Si la cuenta esta suspendida: el enlace no permite acceso y se muestra pantalla de acceso revocado.
- Si el enlace ha caducado: la trabajadora debe solicitar uno nuevo.

### Journey 5: Cierre de sesion
Actor: Trabajadora (Hogar o SAD) | Objetivo: Cerrar sesion de forma segura
1. La trabajadora accede a la opcion de cerrar sesion.
2. La app muestra un dialogo de confirmacion.
3. La trabajadora confirma el cierre de sesion.
4. La app borra los datos de sesion locales e invalida el token en el servidor.
5. La app muestra la pantalla de login.

Estado de exito: La sesion queda cerrada, los datos locales borrados y el token invalidado.

### Journey 6: Acceso revocado (SAD)
Actor: Trabajadora SAD con cuenta suspendida | Objetivo: Entender por que no puede acceder
1. La trabajadora intenta acceder con credenciales validas.
2. El sistema detecta que la cuenta esta suspendida, dada de baja o desactivada.
3. La app muestra una pantalla informativa: "Ya no tienes permisos para acceder a esta aplicacion".
4. La pantalla muestra informacion de contacto o soporte.
5. La trabajadora no puede navegar a ninguna seccion de la app desde esta pantalla.

Estado de exito: La trabajadora entiende la situacion y tiene medios para contactar soporte.

---

## Resultados y Exito

- Cualquier trabajadora Hogar puede registrarse y acceder a la app de forma autonoma.
- Cualquier trabajadora SAD puede activar su cuenta y acceder tras recibir el email del backoffice.
- La sesion se mantiene activa entre usos (hasta 30 dias) sin requerir login repetido.
- La recuperacion de acceso es autoservicio y no requiere intervencion del backoffice.
- Las trabajadoras con cuenta revocada ven informacion clara sobre su situacion.

---

## Instrucciones Inambiguas

### Reglas de comportamiento
- El onboarding se muestra una sola vez, tras el primer login. Su estado de completacion se almacena localmente.
- El contenido del onboarding es general y cubre ambos tipos de contrato (fijo discontinuo e indefinido).
- El permiso de notificaciones push se solicita despues del primer login y antes del onboarding, para vincular el token FCM al usuario concreto.
- El permiso de camara/archivos no se solicita durante el onboarding; se solicita en el momento en que se necesite (por ejemplo, al subir un documento).
- El permiso de ubicacion se solicita durante el onboarding con explicacion clara del uso (fichaje).
- La contrasena debe cumplir: minimo 8 caracteres, al menos una mayuscula y un numero.
- El token de sesion (Sanctum) tiene validez de 30 dias. No hay mecanismo de refresh token en la version actual.
- Si la app recibe una respuesta 401 en cualquier llamada, redirige al login una sola vez (aunque multiples llamadas simultaneas reciban 401).
- Bloqueo temporal tras N intentos fallidos de login (N configurable en servidor).
- El registro solo esta disponible para perfil Hogar. El perfil SAD no tiene registro abierto.

### Destinos de navegacion
| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Splash | Sesion activa y token valido | Pantalla principal (Home) |
| Splash | Sin sesion activa o token expirado | Pantalla de login |
| Login | Credenciales correctas, primer login | Solicitud permiso notificaciones > Onboarding > Home |
| Login | Credenciales correctas, login posterior | Home |
| Login | Cuenta suspendida/revocada (SAD) | Pantalla de acceso revocado |
| Login | Pulsar "Olvidaste tu contrasena?" | Pantalla de recuperacion de acceso |
| Login | Pulsar "Registrarse" (solo Hogar) | Formulario de registro |
| Registro | Registro completado con exito | Solicitud permiso notificaciones > Onboarding > Home |
| Recuperacion | Email enviado con exito | Confirmacion de envio (sin revelar existencia del email) |
| Cierre de sesion | Confirmacion aceptada | Pantalla de login |

---

## Criterios de Aceptacion

### CA-001: Splash con logo de marca <- HU-001
GIVEN la trabajadora abre la app
WHEN la app se inicia
THEN se muestra el logo de la aplicacion sobre fondo de marca durante 2-3 segundos antes de redirigir automaticamente.

### CA-002: Redireccion desde splash <- HU-001
GIVEN la trabajadora ha visto la pantalla de splash
WHEN pasan 2-3 segundos
THEN la app redirige al login si no hay sesion activa, o al Home si hay sesion valida.

### CA-003: Onboarding de 3-5 pantallas <- HU-002
GIVEN la trabajadora ha completado su primer login
WHEN la app muestra el onboarding
THEN se muestran entre 3 y 5 pantallas con los highlights principales de la aplicacion.

### CA-004: Permiso de ubicacion en onboarding <- HU-002
GIVEN la trabajadora esta en el onboarding
WHEN se alcanza el paso de permisos
THEN la app solicita permiso de ubicacion con explicacion clara del uso (fichaje).

### CA-005: Permiso de notificaciones post-login <- HU-002
GIVEN la trabajadora ha completado su primer login
WHEN se inicia el flujo post-login
THEN la app solicita permiso de notificaciones push antes del onboarding para vincular el token al usuario.

### CA-006: Permiso de camara diferido <- HU-002
GIVEN la trabajadora esta en el onboarding o en cualquier flujo previo
WHEN la app muestra los pasos de permisos
THEN no se solicita permiso de camara ni archivos; se solicitara en el momento en que se necesite.

### CA-007: Onboarding mostrado una sola vez <- HU-002
GIVEN la trabajadora ha completado el onboarding
WHEN abre la app en accesos posteriores
THEN el onboarding no se muestra de nuevo; el estado de completacion se almacena localmente.

### CA-008: Contenido onboarding general <- HU-002
GIVEN la trabajadora accede al onboarding
WHEN se muestran las pantallas
THEN el contenido es general y valido para ambos tipos de contrato (fijo discontinuo e indefinido).

### CA-009: Registro Hogar con email y contrasena <- HU-003
GIVEN la trabajadora Hogar esta en la pantalla de registro
WHEN introduce un email valido y una contrasena que cumple los requisitos
THEN se completa el registro y la app inicia sesion automaticamente.

### CA-010: Validacion de contrasena en registro <- HU-003
GIVEN la trabajadora Hogar esta en la pantalla de registro
WHEN introduce una contrasena
THEN la contrasena debe cumplir: minimo 8 caracteres, al menos una mayuscula y al menos un numero.

### CA-011: Errores claros en registro <- HU-003
GIVEN la trabajadora Hogar esta en la pantalla de registro
WHEN un campo no cumple la validacion (email o contrasena)
THEN se muestra un mensaje de error claro y especifico para cada campo.

### CA-012: Asignacion de perfil en registro <- HU-003
GIVEN la trabajadora completa el registro
WHEN el sistema procesa el alta
THEN la trabajadora queda asignada al perfil Hogar.

### CA-013: Activacion de cuenta SAD <- HU-004
GIVEN una trabajadora SAD ha recibido un email de activacion del backoffice
WHEN accede al enlace del email
THEN puede establecer su contrasena y acceder a la app con perfil SAD.

### CA-014: Login con email y contrasena <- HU-005
GIVEN la trabajadora esta en la pantalla de login
WHEN introduce email y contrasena validos
THEN accede a la pantalla principal de la app.

### CA-015: Validacion de formato de email <- HU-005
GIVEN la trabajadora esta en la pantalla de login
WHEN introduce un email
THEN el sistema valida el formato antes de enviar la solicitud.

### CA-016: Error de credenciales incorrectas <- HU-005
GIVEN la trabajadora esta en la pantalla de login
WHEN introduce credenciales incorrectas
THEN se muestra un mensaje de error claro.

### CA-017: Bloqueo temporal por intentos fallidos <- HU-005
GIVEN la trabajadora esta en la pantalla de login
WHEN supera N intentos fallidos (N configurable en servidor)
THEN la cuenta queda bloqueada temporalmente.

### CA-018: Sesion persistente <- HU-007
GIVEN la trabajadora ha iniciado sesion previamente
WHEN abre la app en accesos posteriores
THEN no se requiere login si el token almacenado sigue siendo valido.

### CA-019: Auto-login con token valido <- HU-007
GIVEN la trabajadora tiene un token Sanctum almacenado
WHEN la app arranca y verifica el token con el servidor
THEN si el token es valido, la trabajadora accede directamente a la pantalla principal sin ver la pantalla de login.

### CA-020: Deteccion de token expirado <- HU-007
GIVEN la trabajadora tiene un token Sanctum almacenado
WHEN cualquier llamada a la API devuelve 401
THEN la app redirige al login; si multiples llamadas simultaneas reciben 401, la redireccion ocurre una sola vez.

### CA-021: Enlace de recuperacion <- HU-006
GIVEN la trabajadora esta en la pantalla de login
WHEN pulsa "Olvidaste tu contrasena?"
THEN accede a la pantalla de recuperacion con campo de email.

### CA-022: Envio de recuperacion sin revelar existencia <- HU-006
GIVEN la trabajadora esta en la pantalla de recuperacion
WHEN introduce un email y pulsa enviar
THEN se muestra confirmacion de envio sin revelar si el email existe en el sistema.

### CA-023: Restablecimiento de contrasena <- HU-006
GIVEN la trabajadora ha recibido el email de recuperacion
WHEN accede al enlace de restablecimiento
THEN puede establecer una nueva contrasena que cumpla los mismos requisitos de seguridad que el registro.

### CA-024: Enlace de recuperacion con caducidad <- HU-006
GIVEN la trabajadora ha recibido el enlace de recuperacion
WHEN el enlace ha caducado (tiempo definido por backend)
THEN el enlace no permite restablecer la contrasena y se indica que debe solicitar uno nuevo.

### CA-025: Dialogo de confirmacion al cerrar sesion <- HU-008
GIVEN la trabajadora esta autenticada
WHEN pulsa la opcion de cerrar sesion
THEN se muestra un dialogo de confirmacion antes de proceder.

### CA-026: Borrado de datos al cerrar sesion <- HU-008
GIVEN la trabajadora confirma el cierre de sesion
WHEN se ejecuta el cierre
THEN se borran todos los tokens del almacenamiento seguro, se borran datos de usuaria en cache, se invalida el token en el servidor y se redirige a la pantalla de login.

### CA-027: Pantalla de acceso revocado <- HU-009
GIVEN una trabajadora SAD intenta acceder con credenciales validas pero su cuenta esta suspendida o dada de baja
WHEN el sistema detecta el estado de la cuenta
THEN se muestra una pantalla informativa con mensaje "Ya no tienes permisos para acceder a esta aplicacion" e informacion de contacto o soporte.

### CA-028: Sin navegacion desde acceso revocado <- HU-009
GIVEN la trabajadora esta en la pantalla de acceso revocado
WHEN intenta navegar
THEN no puede acceder a ninguna seccion de la app; no se almacenan tokens ni se mantiene sesion.

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
- Autenticacion biometrica (Face ID, Huella digital)
- Autenticacion de dos factores (2FA)
- Modo offline con sincronizacion
- Gestion de roles y permisos avanzados (el perfil se asigna en registro/activacion)
- El endpoint de refresh token (POST /auth/refresh) esta pendiente de implementar; la sesion se gestiona exclusivamente con el token Sanctum de 30 dias

---

## Asunciones Aplicadas
| Gap origen | Asuncion aplicada |
|------------|-------------------|
| [P-001] | La duracion exacta del splash es de 2-3 segundos, segun indica el PRD, sin animacion adicional configurable |
| [P-002] | El numero maximo de pantallas de onboarding es 3 (valor ideal indicado en el PRD), no 5 |
