# Spec: Autenticacion y Onboarding
> Version: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde /Users/oscar/Documents/AI_labs/Specs Test/project/prd-hogar-sad.md (scope: F-001 via prd-hogar-sad_discovery.md)
> Feature ID: F-001
> Spec monolitico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Profesional de cuidado a domicilio que busca oportunidades laborales a traves de la app CUIDEO | Registrarse con email y contrasena, iniciar sesion, recuperar acceso, completar onboarding, cerrar sesion |
| Trabajadora SAD | Profesional del Servicio de Asistencia Social contratada que gestiona sus servicios a traves de la app Felizvita | Iniciar sesion con credenciales proporcionadas tras activacion desde backoffice, completar onboarding, cerrar sesion, visualizar pantalla de acceso revocado |

---

## Historias de Usuario

### HU-001: Registro de nueva cuenta (Hogar)

Como trabajadora Hogar
quiero registrarme en la aplicacion con mi email y contrasena
para que pueda acceder a las funcionalidades de busqueda de ofertas y gestion de mi perfil profesional

> [INCOMPLETO] -- Pendiente de gap(s): [P-001]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-002: Inicio de sesion

Como trabajadora (Hogar o SAD)
quiero iniciar sesion con mi email y contrasena
para que pueda acceder a mi area personal y a las funcionalidades de la aplicacion

### HU-003: Recuperacion de acceso

Como trabajadora (Hogar o SAD)
quiero recuperar el acceso a mi cuenta cuando olvide mi contrasena
para que pueda volver a acceder a la aplicacion sin depender de soporte

### HU-004: Onboarding post-login

Como trabajadora (Hogar o SAD)
quiero ver una presentacion de las funcionalidades principales de la app tras mi primer inicio de sesion
para que entienda como usar la aplicacion y conceda los permisos necesarios

### HU-005: Gestion de sesion persistente

Como trabajadora (Hogar o SAD)
quiero que mi sesion se mantenga activa entre usos de la aplicacion
para que no tenga que introducir mis credenciales cada vez que abro la app

### HU-006: Cierre de sesion

Como trabajadora (Hogar o SAD)
quiero poder cerrar mi sesion de forma voluntaria
para que mis datos queden protegidos si comparto el dispositivo o quiero cambiar de cuenta

### HU-007: Acceso revocado (SAD)

Como trabajadora SAD cuya cuenta ha sido suspendida o dada de baja
quiero ver una pantalla informativa clara cuando intento acceder
para que entienda que ya no tengo acceso y sepa como contactar con soporte

---

## Recorridos de Usuario

### Journey 1: Registro de nueva cuenta (solo Hogar)

Actor: Trabajadora Hogar | Objetivo: Crear su cuenta y acceder a la aplicacion por primera vez

1. La trabajadora abre la aplicacion por primera vez y ve la pantalla de splash con el logo de la app durante aproximadamente 2 segundos
2. Al no tener sesion activa, la app muestra la pantalla de inicio de sesion
3. La trabajadora pulsa el enlace "Registrarse" o similar
4. La app muestra el formulario de registro con campos de email y contrasena
5. La trabajadora introduce su email y elige una contrasena que cumpla los requisitos minimos de seguridad (minimo 8 caracteres, al menos una mayuscula y un numero)
6. La trabajadora envia el formulario
7. Si los datos son validos, el registro se completa y la sesion se inicia automaticamente
8. La app muestra la solicitud de permiso de notificaciones push con explicacion del uso
9. A continuacion, se muestran las pantallas de onboarding (3 pantallas con las funcionalidades principales)
10. Durante el onboarding, se solicita permiso de ubicacion con explicacion clara de su uso para fichaje
11. Al completar el onboarding, la trabajadora accede a la pantalla principal (home) con los accesos directos de Hogar

Estado de exito: La trabajadora ha creado su cuenta, concedido permisos y ve la pantalla principal de la aplicacion con su perfil Hogar activo.

Flujos alternativos:
- Si el email ya esta registrado -> se muestra un mensaje de error indicando que el email ya tiene una cuenta asociada
- Si la contrasena no cumple los requisitos -> se muestra un mensaje de error con los requisitos incumplidos
- Si hay un error de validacion en el formulario -> se muestra el error especifico junto al campo afectado
- Si la trabajadora rechaza el permiso de notificaciones -> el onboarding continua sin bloquear; la trabajadora podra habilitarlas posteriormente desde la configuracion del dispositivo

> [INCOMPLETO] -- Pendiente de gap(s): [P-001]. Los campos exactos del formulario de registro estan pendientes de definicion.

### Journey 2: Primer acceso de trabajadora SAD (activacion)

Actor: Trabajadora SAD | Objetivo: Acceder a la aplicacion por primera vez tras recibir sus credenciales

1. La trabajadora SAD recibe un email de activacion desde el backoffice (gestion externa a la app)
2. La trabajadora establece su contrasena a traves del proceso de activacion externo
3. La trabajadora abre la app y ve la pantalla de splash con el logo durante aproximadamente 2 segundos
4. Al no tener sesion activa, la app muestra la pantalla de inicio de sesion
5. La trabajadora introduce su email y la contrasena que establecio en el paso de activacion
6. La app verifica las credenciales y, si son correctas, inicia la sesion
7. La app muestra la solicitud de permiso de notificaciones push
8. Se muestran las pantallas de onboarding (3 pantallas con funcionalidades principales, contenido general valido para ambos tipos de contrato)
9. Durante el onboarding, se solicita permiso de ubicacion
10. Al completar el onboarding, la trabajadora accede a la pantalla principal (home) con los accesos directos de SAD

Estado de exito: La trabajadora SAD ha iniciado sesion por primera vez, completado el onboarding y ve la pantalla principal con su perfil SAD activo.

Flujos alternativos:
- Si las credenciales son incorrectas -> se muestra un mensaje de error claro
- Si la cuenta esta suspendida o dada de baja -> se muestra la pantalla de acceso revocado (ver Journey 7)

### Journey 3: Inicio de sesion recurrente

Actor: Trabajadora (Hogar o SAD) | Objetivo: Acceder a la app en usos posteriores al registro

1. La trabajadora abre la aplicacion
2. Se muestra la pantalla de splash durante aproximadamente 2 segundos
3. La app verifica si existe una sesion activa valida
4. Si la sesion es valida (no han pasado mas de 30 dias desde el ultimo inicio de sesion), la app redirige directamente a la pantalla principal sin mostrar la pantalla de login
5. Si la sesion ha expirado, la app muestra la pantalla de inicio de sesion
6. La trabajadora introduce email y contrasena
7. Si las credenciales son correctas, accede a la pantalla principal
8. El onboarding no se muestra de nuevo

Estado de exito: La trabajadora accede a su pantalla principal en menos de 3 segundos si tiene sesion activa, o tras introducir sus credenciales si la sesion ha expirado.

Flujos alternativos:
- Si la sesion fue revocada por el servidor (baja, suspension) -> la app muestra la pantalla de acceso revocado (SAD) o redirige al login con mensaje de error (Hogar)
- Si las credenciales son incorrectas -> se muestra mensaje de error claro
- Tras N intentos fallidos consecutivos, la cuenta se bloquea temporalmente y se muestra un mensaje indicando el bloqueo y el tiempo estimado de espera

### Journey 4: Recuperacion de acceso

Actor: Trabajadora (Hogar o SAD) | Objetivo: Restablecer su contrasena olvidada

1. La trabajadora esta en la pantalla de inicio de sesion y no recuerda su contrasena
2. La trabajadora pulsa el enlace "Olvidaste tu contrasena?" o similar
3. La app muestra una pantalla con un campo de email
4. La trabajadora introduce su email y confirma
5. La app muestra un mensaje de confirmacion indicando que se ha enviado un email de recuperacion (sin revelar si el email existe en el sistema, por seguridad)
6. La trabajadora abre el email y pulsa el enlace de restablecimiento
7. La app muestra la pantalla para establecer una nueva contrasena
8. La trabajadora introduce una nueva contrasena que cumpla los requisitos de seguridad (mismos que el registro: minimo 8 caracteres, al menos una mayuscula y un numero)
9. La contrasena se actualiza y la trabajadora puede iniciar sesion con la nueva contrasena

Estado de exito: La trabajadora ha restablecido su contrasena y puede acceder a la aplicacion con sus nuevas credenciales.

Flujos alternativos:
- Si el enlace de recuperacion ha caducado -> se muestra un mensaje indicando que el enlace ya no es valido e invitando a solicitar uno nuevo
- Si la nueva contrasena no cumple los requisitos -> se muestran los requisitos incumplidos
- Si la cuenta esta dada de baja o suspendida -> el enlace no permite el acceso y se muestra la pantalla de acceso revocado

### Journey 5: Onboarding post-primer-login

Actor: Trabajadora (Hogar o SAD) | Objetivo: Conocer las funcionalidades de la app y conceder permisos

1. Tras el primer inicio de sesion exitoso, antes de acceder al home, la app solicita permiso de notificaciones push con una explicacion clara del beneficio
2. La trabajadora concede o rechaza el permiso de notificaciones
3. La app muestra 3 pantallas de onboarding con los highlights principales de la aplicacion (contenido general valido para ambos tipos de contrato: fijo discontinuo e indefinido)
4. Durante el onboarding, se solicita permiso de ubicacion con explicacion de su uso para el fichaje de entrada y salida en servicios
5. La trabajadora puede avanzar por las pantallas de onboarding y completar el flujo
6. Al finalizar el onboarding, la app redirige a la pantalla principal (home)
7. El onboarding no se vuelve a mostrar en accesos posteriores

Estado de exito: La trabajadora ha visto las funcionalidades principales, ha tenido la oportunidad de conceder permisos y accede al home.

Flujos alternativos:
- Si la trabajadora rechaza el permiso de notificaciones -> el onboarding continua normalmente; no recibira notificaciones push hasta habilitarlas desde la configuracion del dispositivo
- Si la trabajadora rechaza el permiso de ubicacion -> el onboarding continua; las funcionalidades que requieran ubicacion (fichaje) mostraran un aviso en el momento de uso
- El permiso de camara/archivos no se solicita en el onboarding; se solicita en el momento de uso (al subir un documento, foto de perfil, etc.)

### Journey 6: Cierre de sesion

Actor: Trabajadora (Hogar o SAD) | Objetivo: Cerrar su sesion de forma voluntaria

1. La trabajadora navega a la seccion de perfil o configuracion donde se encuentra la opcion de cerrar sesion
2. La trabajadora pulsa "Cerrar sesion"
3. La app muestra un dialogo de confirmacion preguntando si desea cerrar sesion
4. La trabajadora confirma
5. La app borra los datos de sesion del dispositivo e informa al servidor de la desconexion
6. La app redirige a la pantalla de inicio de sesion

Estado de exito: La sesion se ha cerrado, los datos locales de sesion se han borrado y la trabajadora ve la pantalla de login.

Flujos alternativos:
- Si la trabajadora cancela en el dialogo de confirmacion -> permanece en la pantalla actual con la sesion activa

### Journey 7: Acceso revocado (solo SAD)

Actor: Trabajadora SAD con cuenta suspendida o dada de baja | Objetivo: Entender que no tiene acceso y saber como proceder

1. La trabajadora SAD abre la app o intenta iniciar sesion
2. La app detecta que la cuenta esta suspendida, dada de baja o desactivada
3. La app muestra una pantalla informativa con el mensaje "Ya no tienes permisos para acceder a esta aplicacion" (o similar)
4. La pantalla muestra informacion de contacto o soporte para que la trabajadora pueda resolver la situacion
5. No se permite navegar a ninguna seccion de la app desde esta pantalla
6. No se almacenan datos de sesion en el dispositivo

Estado de exito: La trabajadora ve un mensaje claro de acceso denegado con informacion de contacto, sin posibilidad de navegar a otras secciones.

Flujos alternativos:
- Si la trabajadora intenta recuperar acceso desde esta pantalla -> el enlace de recuperacion no permite el acceso mientras la cuenta siga suspendida/dada de baja

---

## Resultados y Exito

La feature se considera completa cuando:

1. **Registro Hogar**: una trabajadora Hogar puede crear su cuenta con email y contrasena y acceder a la app en un unico flujo continuo
2. **Primer acceso SAD**: una trabajadora SAD puede iniciar sesion por primera vez con las credenciales que establecio durante el proceso de activacion externo
3. **Inicio de sesion**: cualquier trabajadora con credenciales validas accede a su home correcto (Hogar o SAD) tras introducir email y contrasena
4. **Sesion persistente**: la sesion se mantiene activa durante 30 dias sin requerir nuevo login, y la verificacion al arrancar es transparente para la usuaria
5. **Recuperacion**: una trabajadora que olvida su contrasena puede restablecerla via email y volver a acceder
6. **Onboarding**: se muestra una unica vez tras el primer login y permite conceder permisos de notificaciones y ubicacion
7. **Cierre de sesion**: la trabajadora puede cerrar sesion voluntariamente con confirmacion previa, y los datos de sesion se borran del dispositivo
8. **Acceso revocado (SAD)**: una cuenta suspendida o dada de baja muestra pantalla informativa sin permitir navegacion

---

## Instrucciones Inambiguas

### Reglas de comportamiento

1. **Diferenciacion de perfiles**: la app asigna automaticamente a la usuaria al perfil correcto (Hogar o SAD) segun los datos de su cuenta. La pantalla principal y los accesos directos se adaptan al perfil asignado.

2. **Orden del flujo post-primer-login**: login -> solicitud de permiso de notificaciones push -> pantallas de onboarding (con solicitud de permiso de ubicacion) -> home. Este orden garantiza que el permiso de notificaciones se solicita antes de cualquier contenido de onboarding.

3. **Permiso de camara/archivos**: no se solicita durante el onboarding. Se solicita en el momento en que la usuaria necesita acceder a la camara o a archivos del dispositivo (al subir un documento, capturar foto de perfil, etc.).

4. **Requisitos de contrasena**: minimo 8 caracteres, al menos una mayuscula y al menos un numero. Aplica tanto al registro como a la recuperacion de contrasena.

5. **Bloqueo por intentos fallidos**: tras un numero configurable de intentos fallidos consecutivos de inicio de sesion, la cuenta se bloquea temporalmente. La app muestra un mensaje indicando el bloqueo y el tiempo estimado de espera. El numero de intentos y la duracion del bloqueo los define el servidor.

6. **Sesion de 30 dias**: la sesion se mantiene activa durante 30 dias desde el ultimo inicio de sesion. Si expira, la app redirige a la pantalla de login al abrir la aplicacion. Si la sesion es revocada por el servidor antes de los 30 dias, el efecto es el mismo.

7. **Verificacion de sesion al arrancar**: al abrir la app, se verifica la validez de la sesion. Si la sesion es invalida (expirada o revocada), se redirige al login. Si multiples verificaciones simultaneas detectan sesion invalida, la redireccion al login se ejecuta una sola vez.

8. **Contenido del onboarding**: general y valido para ambos tipos de contrato (fijo discontinuo e indefinido), ya que las trabajadoras pueden rotar entre estados.

9. **Confirmacion de email de recuperacion**: al solicitar recuperacion de acceso, la app muestra un mensaje generico de confirmacion sin revelar si el email existe en el sistema (por seguridad).

10. **Caducidad del enlace de recuperacion**: el enlace de recuperacion de contrasena tiene una caducidad definida por el servidor. Si ha caducado, se informa a la usuaria e invita a solicitar uno nuevo.

11. **Activacion SAD (proceso externo)**: la activacion de cuentas SAD (creacion de cuenta y envio de email de activacion) es un proceso gestionado por un servicio externo al ambito de la app. La app solo se encarga del inicio de sesion posterior con las credenciales establecidas durante la activacion.

12. **Acceso revocado**: la deteccion de cuenta suspendida o dada de baja se produce al verificar la sesion o al intentar iniciar sesion. Aplica solo a perfil SAD. Para Hogar, una cuenta invalidada se trata como credenciales incorrectas con mensaje de error.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Pantalla de splash | Sesion activa y valida | Pantalla principal (home) adaptada al perfil |
| Pantalla de splash | Sin sesion activa o sesion expirada | Pantalla de inicio de sesion |
| Pantalla de inicio de sesion | Credenciales correctas (primer login) | Solicitud de permiso de notificaciones -> Onboarding -> Home |
| Pantalla de inicio de sesion | Credenciales correctas (login recurrente) | Pantalla principal (home) adaptada al perfil |
| Pantalla de inicio de sesion | Credenciales incorrectas | Permanece en login con mensaje de error |
| Pantalla de inicio de sesion | Cuenta bloqueada por intentos fallidos | Permanece en login con mensaje de bloqueo temporal |
| Pantalla de inicio de sesion | Cuenta SAD suspendida/dada de baja | Pantalla de acceso revocado |
| Pantalla de inicio de sesion | Pulsa "Registrarse" | Pantalla de registro (solo Hogar) |
| Pantalla de inicio de sesion | Pulsa "Olvidaste tu contrasena?" | Pantalla de recuperacion de acceso |
| Pantalla de registro | Registro exitoso | Solicitud de permiso de notificaciones -> Onboarding -> Home |
| Pantalla de registro | Error de validacion | Permanece en registro con mensajes de error |
| Pantalla de recuperacion | Email enviado | Pantalla de confirmacion de envio |
| Enlace de recuperacion (email) | Enlace valido | Pantalla de nueva contrasena |
| Enlace de recuperacion (email) | Enlace caducado | Pantalla informativa de enlace expirado con opcion de solicitar nuevo |
| Enlace de recuperacion (email) | Cuenta suspendida/dada de baja | Pantalla de acceso revocado |
| Pantalla de nueva contrasena | Contrasena actualizada | Pantalla de inicio de sesion (para que inicie sesion con la nueva contrasena) |
| Onboarding (ultima pantalla) | Completado | Pantalla principal (home) |
| Cualquier pantalla (sesion activa) | Sesion detectada como invalida | Pantalla de inicio de sesion |
| Perfil / Configuracion | Pulsa "Cerrar sesion" y confirma | Pantalla de inicio de sesion |
| Pantalla de acceso revocado | Ninguna accion de navegacion permitida | Permanece en pantalla de acceso revocado |

---

## Criterios de Aceptacion

### CA-001: Visualizacion de splash con logo de marca <- HU-005
GIVEN la trabajadora abre la aplicacion
WHEN la pantalla de splash se muestra
THEN aparece el logo de la aplicacion sobre fondo de marca durante aproximadamente 2 segundos antes de redirigir automaticamente

### CA-002: Redireccion desde splash con sesion activa <- HU-005
GIVEN la trabajadora tiene una sesion activa y valida (menos de 30 dias desde el ultimo inicio de sesion)
WHEN la pantalla de splash completa su visualizacion
THEN la aplicacion muestra directamente la pantalla principal (home) adaptada al perfil de la trabajadora sin mostrar la pantalla de login

### CA-003: Redireccion desde splash sin sesion activa <- HU-005
GIVEN la trabajadora no tiene sesion activa o su sesion ha expirado
WHEN la pantalla de splash completa su visualizacion
THEN la aplicacion muestra la pantalla de inicio de sesion

### CA-004: Registro Hogar con email y contrasena <- HU-001
GIVEN la trabajadora Hogar esta en la pantalla de registro
WHEN introduce un email valido y una contrasena que cumple los requisitos (minimo 8 caracteres, al menos una mayuscula y un numero) y envia el formulario
THEN el registro se completa, la sesion se inicia automaticamente y la app procede al flujo de onboarding

> [INCOMPLETO] -- Pendiente de gap(s): [P-001]. Los campos exactos del formulario de registro estan pendientes de definicion. Este CA cubre email y contrasena, pero pueden existir campos adicionales.

### CA-005: Validacion de errores en registro <- HU-001
GIVEN la trabajadora Hogar esta en la pantalla de registro
WHEN introduce datos que no cumplen las validaciones (email con formato invalido, contrasena que no cumple requisitos, email ya registrado)
THEN se muestran mensajes de error claros y especificos junto al campo afectado sin perder los datos ya introducidos

> [INCOMPLETO] -- Pendiente de gap(s): [P-001]. La lista completa de validaciones depende de los campos definitivos del formulario.

### CA-006: Inicio de sesion con credenciales correctas <- HU-002
GIVEN la trabajadora esta en la pantalla de inicio de sesion
WHEN introduce su email y contrasena correctos y confirma
THEN la sesion se inicia y la app redirige a la pantalla principal (home) adaptada a su perfil (Hogar o SAD)

### CA-007: Error de credenciales incorrectas <- HU-002
GIVEN la trabajadora esta en la pantalla de inicio de sesion
WHEN introduce credenciales incorrectas (email o contrasena erroneos)
THEN la app muestra un mensaje de error claro indicando que las credenciales son incorrectas, sin revelar cual de los dos campos es el erroneo

### CA-008: Bloqueo temporal por intentos fallidos <- HU-002
GIVEN la trabajadora ha introducido credenciales incorrectas un numero consecutivo de veces igual al umbral configurado en el servidor
WHEN intenta iniciar sesion una vez mas
THEN la app muestra un mensaje indicando que la cuenta esta temporalmente bloqueada y el tiempo estimado de espera

### CA-009: Sesion persistente de 30 dias <- HU-005
GIVEN la trabajadora ha iniciado sesion hace menos de 30 dias y no ha cerrado sesion manualmente
WHEN abre la aplicacion
THEN la app verifica la sesion y la redirige directamente a la pantalla principal sin solicitar credenciales

### CA-010: Sesion expirada tras 30 dias <- HU-005
GIVEN la trabajadora no ha iniciado sesion en los ultimos 30 dias
WHEN abre la aplicacion
THEN la app muestra la pantalla de inicio de sesion para que introduzca sus credenciales de nuevo

### CA-011: Deteccion de sesion revocada <- HU-005
GIVEN la trabajadora tiene una sesion que ha sido revocada por el servidor (baja, suspension, invalidacion)
WHEN la app intenta verificar la sesion al arrancar o durante el uso
THEN la app redirige a la pantalla de inicio de sesion (o a la pantalla de acceso revocado si es SAD con cuenta suspendida)

### CA-012: Redireccion unica ante multiples detecciones de sesion invalida <- HU-005
GIVEN la app ejecuta multiples verificaciones simultaneas y varias detectan sesion invalida
WHEN se resuelven las verificaciones
THEN la redireccion al login se ejecuta una sola vez, sin pantallas duplicadas ni parpadeos

### CA-013: Solicitud de recuperacion de acceso <- HU-003
GIVEN la trabajadora esta en la pantalla de recuperacion de acceso
WHEN introduce su email y confirma la solicitud
THEN la app muestra un mensaje de confirmacion indicando que se ha enviado un email de recuperacion, sin revelar si el email existe en el sistema

### CA-014: Restablecimiento de contrasena via enlace <- HU-003
GIVEN la trabajadora ha recibido un email de recuperacion con enlace valido
WHEN pulsa el enlace y establece una nueva contrasena que cumple los requisitos de seguridad
THEN la contrasena se actualiza y la trabajadora puede iniciar sesion con la nueva contrasena

### CA-015: Enlace de recuperacion caducado <- HU-003
GIVEN la trabajadora ha recibido un email de recuperacion
WHEN pulsa el enlace despues de que haya caducado
THEN la app muestra un mensaje indicando que el enlace ya no es valido e invita a solicitar uno nuevo

### CA-016: Recuperacion con cuenta suspendida <- HU-003
GIVEN la trabajadora tiene una cuenta dada de baja o suspendida
WHEN pulsa el enlace de recuperacion de contrasena
THEN el enlace no permite el acceso y se muestra la pantalla de acceso revocado

### CA-017: Permiso de notificaciones post-primer-login <- HU-004
GIVEN la trabajadora ha iniciado sesion por primera vez (primer login tras registro o primera activacion)
WHEN el login es exitoso
THEN la app solicita permiso de notificaciones push con una explicacion clara del beneficio antes de mostrar el onboarding

### CA-018: Pantallas de onboarding tras primer login <- HU-004
GIVEN la trabajadora ha concedido o rechazado el permiso de notificaciones en su primer login
WHEN procede al onboarding
THEN se muestran 3 pantallas de bienvenida con los highlights principales de la aplicacion y contenido general valido para ambos tipos de contrato

### CA-019: Solicitud de permiso de ubicacion durante onboarding <- HU-004
GIVEN la trabajadora esta en las pantallas de onboarding
WHEN llega al punto de solicitud de permiso de ubicacion
THEN la app solicita permiso de ubicacion con una explicacion clara de su uso para el fichaje de entrada y salida

### CA-020: Onboarding mostrado una sola vez <- HU-004
GIVEN la trabajadora ha completado el onboarding en su primer login
WHEN cierra y vuelve a abrir la app o inicia sesion en posteriores ocasiones
THEN el onboarding no se vuelve a mostrar

### CA-021: Confirmacion antes de cerrar sesion <- HU-006
GIVEN la trabajadora esta autenticada y navega a la opcion de cerrar sesion
WHEN pulsa "Cerrar sesion"
THEN la app muestra un dialogo de confirmacion preguntando si desea cerrar sesion

### CA-022: Ejecucion del cierre de sesion <- HU-006
GIVEN la trabajadora ha confirmado que desea cerrar sesion en el dialogo de confirmacion
WHEN la confirmacion se procesa
THEN la app borra todos los datos de sesion del dispositivo, informa al servidor de la desconexion y redirige a la pantalla de inicio de sesion

### CA-023: Cancelacion del cierre de sesion <- HU-006
GIVEN la trabajadora ha pulsado "Cerrar sesion" y se muestra el dialogo de confirmacion
WHEN pulsa "Cancelar" en el dialogo
THEN el dialogo se cierra y la trabajadora permanece en la pantalla actual con la sesion activa

### CA-024: Pantalla de acceso revocado (SAD) <- HU-007
GIVEN una trabajadora SAD cuya cuenta ha sido suspendida, dada de baja o desactivada intenta acceder a la app
WHEN la app detecta el estado de cuenta revocada (al iniciar sesion o al verificar sesion al arrancar)
THEN se muestra una pantalla informativa con mensaje claro ("Ya no tienes permisos para acceder a esta aplicacion" o similar) e informacion de contacto/soporte

### CA-025: Bloqueo de navegacion en acceso revocado <- HU-007
GIVEN la trabajadora SAD esta en la pantalla de acceso revocado
WHEN intenta navegar a cualquier seccion de la app
THEN no se permite la navegacion; la trabajadora permanece en la pantalla de acceso revocado

### CA-026: No persistencia de sesion en acceso revocado <- HU-007
GIVEN una trabajadora SAD ha sido redirigida a la pantalla de acceso revocado
WHEN la pantalla se muestra
THEN no se almacenan ni mantienen datos de sesion en el dispositivo

### CA-027: Asignacion automatica de perfil <- HU-002
GIVEN una trabajadora inicia sesion con credenciales validas
WHEN la sesion se establece
THEN la app asigna automaticamente el perfil correcto (Hogar o SAD) segun los datos de la cuenta y adapta la pantalla principal en consecuencia

---

## Checklist de Validacion

- [x] Actores identificados (Trabajadora Hogar y Trabajadora SAD)
- [x] Flujos principales descritos paso a paso (7 journeys)
- [x] Estados de exito definidos para cada flujo
- [x] Edge cases documentados (enlace caducado, cuenta bloqueada, cuenta revocada, permisos rechazados, sesion revocada remotamente, multiples detecciones simultaneas)
- [x] Estados de error definidos (credenciales incorrectas, validacion de formulario, bloqueo temporal, enlace expirado)
- [ ] Ambiguedades resueltas -- Pendiente: campos del formulario de registro Hogar [P-001]
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- **Autenticacion biometrica** (Face ID, huella digital): excluida del MVP, posible fase futura
- **Autenticacion de dos factores (2FA)**: excluida del MVP, posible fase futura
- **Proceso de activacion de cuentas SAD**: la creacion de cuentas SAD y el envio del email de activacion son gestion del backoffice y un servicio externo. Esta feature solo cubre el inicio de sesion posterior con las credenciales establecidas
- **Gestion de contrasenas desde la app (cambio voluntario)**: la trabajadora puede restablecer su contrasena via email de recuperacion, pero no hay funcionalidad de "cambiar contrasena" desde dentro de la app autenticada en esta version
- **Perfil de la trabajadora y datos personales**: cubierto por la feature F-010 (profile-and-documents)
- **Notificaciones push (recepcion y gestion)**: cubierto por la feature F-012 (push-notifications). Esta feature solo cubre la solicitud de permiso durante el onboarding

---

## Items Pendientes

> Este spec tiene gaps **criticos** sin resolver. Las HUs afectadas estan marcadas `[INCOMPLETO]` y `/wf-prepare-plan` quedara bloqueado hasta que se resuelvan.
> Para resolverlos: edita este spec respondiendo los gaps, luego ejecuta `/wf-spec-validate <path>_spec.md`.

### [P-001][CRITICO] Campos del formulario de registro de trabajadoras Hogar
- **Afecta**: [HU-001]
- **Pregunta**: Que campos se solicitan en el formulario de registro de trabajadoras Hogar? Solo email y contrasena, o tambien nombre, telefono u otros datos? El perfil se completa en un paso posterior?
- **Respuesta**: [CRITICO]_(pendiente)_

---

## Asunciones Aplicadas

- **[A-001]**: El proceso de activacion de cuentas SAD (creacion de cuenta desde backoffice y envio de email de activacion) es completamente externo a la app. La app solo se encarga del inicio de sesion posterior. Justificacion: respuesta del cliente en el analysis [P-003]: "no hay nada a implementar por parte de la app. Esa gestion es por parte de otro servicio, en la app solamente tendra que hacer el inicio de sesion con la nueva contrasena y ya esta."

- **[A-002]**: Se muestran 3 pantallas de onboarding con contenido generico: 1) Bienvenida y descripcion general de la app, 2) Funcionalidades principales, 3) Primeros pasos. El contenido exacto se ajustara cuando diseno proporcione los wireframes. Justificacion: gap informativo [P-011] del analysis sin respuesta del cliente; se aplica la asuncion por defecto.

- **[A-003]**: La pantalla de splash se muestra durante un tiempo fijo de aproximadamente 2 segundos mientras la aplicacion realiza la verificacion de sesion. Si la verificacion tarda mas de 2 segundos, la splash se extiende hasta completarla. Justificacion: gap informativo [P-012] del analysis sin respuesta del cliente; se aplica la asuncion por defecto.
