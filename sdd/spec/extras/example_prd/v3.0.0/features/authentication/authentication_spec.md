# Spec: Autenticacion y Onboarding

> Version: 1.0 | Fecha: 2026-04-05
> Spec monolitico origen: prd-hogar-sad_spec.md
> Feature ID: F-001

---

## Actores

| Actor | Descripcion | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades de empleo a traves de la app CUIDEO (tema azul) | Registrarse, iniciar sesion, recuperar acceso, cerrar sesion, completar onboarding |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona sus servicios asignados a traves de la app Felizvita (tema verde) | Activar cuenta, iniciar sesion, recuperar acceso, cerrar sesion, completar onboarding, ver pantalla de acceso revocado |
| Sistema | El propio sistema automatizado que ejecuta acciones programadas sin intervencion humana | Gestionar expiracion de sesiones |
| Coordinadora / Backoffice | Profesional de gestion interna que supervisa a las trabajadoras. No usa la app movil directamente; interactua a traves del sistema de backoffice | Enviar email de activacion de cuenta (SAD), revocar/suspender cuentas |

---

## Historias de Usuario

### HU-001: Pantalla de splash
Como trabajadora (Hogar o SAD)
quiero ver una pantalla de bienvenida con el logo de la app al abrirla
para que tenga una experiencia de carga fluida y sepa que la app esta iniciando correctamente.

### HU-002: Registro de cuenta (Hogar)
Como trabajadora Hogar
quiero registrarme en la app con mi email y contrasena
para que pueda acceder a las ofertas de trabajo y funcionalidades de la app.

### HU-003: Pantallas de bienvenida (onboarding)
Como trabajadora (Hogar o SAD)
quiero ver una guia de bienvenida tras mi primer inicio de sesion
para que entienda las funcionalidades principales de la app antes de empezar a usarla.

> ⚠ [INCOMPLETO] — Pendiente de gap(s): [P-001]. Responde en el `_analysis.md` y ejecuta `/wf-spec-delta resolve` para completar.

### HU-004: Activacion de cuenta (SAD)
Como trabajadora SAD
quiero activar mi cuenta a traves de un enlace de email enviado desde el backoffice
para que pueda establecer mis credenciales y acceder a la app por primera vez.

### HU-005: Inicio de sesion
Como trabajadora (Hogar o SAD)
quiero iniciar sesion con mi email y contrasena
para que pueda acceder a las funcionalidades de la app de forma segura.

### HU-006: Sesion persistente
Como trabajadora (Hogar o SAD)
quiero que mi sesion se mantenga activa entre usos de la app
para que no tenga que iniciar sesion cada vez que abro la app.

### HU-007: Recuperacion de acceso
Como trabajadora (Hogar o SAD)
quiero poder recuperar el acceso a mi cuenta si olvido mi contrasena
para que no pierda el acceso a la app de forma permanente.

### HU-008: Cierre de sesion
Como trabajadora (Hogar o SAD)
quiero poder cerrar mi sesion de forma explicita
para que nadie mas pueda acceder a mi cuenta desde mi dispositivo.

### HU-009: Pantalla de acceso revocado (SAD)
Como trabajadora SAD cuya cuenta ha sido suspendida o dada de baja
quiero ver una pantalla informativa clara cuando intento acceder
para que entienda por que no puedo entrar y sepa como contactar a soporte.

---

## Recorridos de Usuario

### Journey 1: Registro y primer acceso (Hogar)
Actor: Trabajadora Hogar | Objetivo: Registrarse en la app y acceder por primera vez

1. La trabajadora abre la app CUIDEO y ve la pantalla de splash con el logo azul.
2. Tras la pantalla de splash, la app muestra la pantalla de inicio de sesion (no hay sesion previa).
3. La trabajadora pulsa "Registrarse".
4. La trabajadora introduce su email y elige una contrasena (minimo 8 caracteres, al menos una mayuscula y un numero).
5. La trabajadora envia el formulario de registro.
6. El sistema valida los datos y completa el registro. La trabajadora queda autenticada automaticamente.
7. El sistema solicita permiso de notificaciones push.
8. Se muestra el flujo de bienvenida (onboarding) con pantallas informativas sobre las funcionalidades de la app.
9. La trabajadora completa el onboarding (se muestra solo una vez).
10. La trabajadora accede al panel principal (home) con accesos directos a: Ofertas, Mi Disponibilidad, Perfil, Comunicacion.

Estado de exito: La trabajadora ha creado su cuenta, ha completado el onboarding y esta en el panel principal con todas las funcionalidades accesibles.

Flujos alternativos:
- Si el email ya esta registrado: el sistema muestra un mensaje de error indicando que el email ya existe.
- Si la contrasena no cumple los requisitos: se muestra el error de validacion en linea.

### Journey 2: Activacion y primer acceso (SAD)
Actor: Trabajadora SAD | Objetivo: Activar su cuenta y acceder por primera vez

1. La trabajadora recibe un email de activacion enviado desde el backoffice.
2. La trabajadora abre el enlace de activacion del email.
3. El enlace la lleva a una pantalla donde puede establecer su contrasena (el email ya esta preconfigurado).
4. La trabajadora establece su contrasena y confirma.
5. La trabajadora abre la app Felizvita y ve la pantalla de splash con el logo verde.
6. La app muestra la pantalla de inicio de sesion.
7. La trabajadora introduce su email y contrasena.
8. El sistema valida las credenciales y establece la sesion.
9. El sistema solicita permiso de notificaciones push.
10. Se muestra el flujo de bienvenida (onboarding).
11. La trabajadora completa el onboarding y accede al panel principal (home) con accesos directos priorizando el servicio activo y el fichaje.

Estado de exito: La trabajadora SAD ha activado su cuenta, ha iniciado sesion y esta en el panel principal con todas las funcionalidades accesibles.

Flujos alternativos:
- Si la cuenta ha sido revocada o suspendida: se muestra la pantalla de acceso revocado con mensaje "Ya no tienes permisos para acceder a esta aplicacion" e informacion de contacto de soporte.

### Journey 3: Inicio de sesion habitual
Actor: Trabajadora (Hogar o SAD) | Objetivo: Acceder a la app tras haberla cerrado

1. La trabajadora abre la app y ve la pantalla de splash.
2. El sistema verifica la validez de la sesion almacenada.
3. Si la sesion es valida: la app navega directamente al panel principal sin mostrar la pantalla de inicio de sesion.
4. Si la sesion ha expirado o ha sido revocada: la app muestra la pantalla de inicio de sesion.

Estado de exito: La trabajadora accede al panel principal sin friccion si tiene sesion valida, o puede iniciar sesion si la sesion expiro.

Flujos alternativos:
- Si la cuenta ha sido dada de baja (solo SAD): se muestra la pantalla de acceso revocado.

### Journey 4: Recuperacion de acceso
Actor: Trabajadora (Hogar o SAD) | Objetivo: Recuperar el acceso a su cuenta tras olvidar la contrasena

1. La trabajadora esta en la pantalla de inicio de sesion y pulsa "Olvidaste tu contrasena?" o similar.
2. El sistema muestra la pantalla de recuperacion con un campo de email.
3. La trabajadora introduce su email y pulsa enviar.
4. El sistema muestra un mensaje de confirmacion generico (sin revelar si el email existe en el sistema).
5. Si el email es valido, la trabajadora recibe un email con un enlace de recuperacion.
6. La trabajadora abre el enlace y accede a la pantalla de establecer nueva contrasena.
7. La trabajadora introduce su nueva contrasena (cumpliendo los mismos requisitos de seguridad que el registro).
8. El sistema confirma el cambio y la trabajadora puede iniciar sesion con la nueva contrasena.

Estado de exito: La trabajadora ha restablecido su contrasena y puede acceder nuevamente a la app.

Flujos alternativos:
- Si el enlace ha caducado: el sistema informa que el enlace ya no es valido e invita a solicitar uno nuevo.
- Si la cuenta esta dada de baja o suspendida: el enlace no permite el acceso y se muestra la pantalla de acceso revocado.

---

## Resultados y Exito

- **Acceso y sesion**: Las trabajadoras pueden registrarse (Hogar) o activar su cuenta (SAD), iniciar sesion y mantener una sesion persistente sin necesidad de autenticarse cada vez. La sesion solo se interrumpe por cierre explicito, revocacion de cuenta o expiracion por inactividad prolongada.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

- **Doble perfil**: Existen dos aplicaciones diferenciadas por marca (CUIDEO tema azul para Hogar, Felizvita tema verde para SAD). Cada app muestra unicamente las funcionalidades correspondientes a su perfil.
- **Sesion persistente**: La sesion se mantiene activa tras el primer inicio de sesion. Solo se solicita nuevo login si la trabajadora cierra sesion explicitamente, si la cuenta es revocada, o tras un periodo de inactividad prolongado configurado por el sistema.
- **Verificacion de sesion al arrancar**: Al abrir la app, el sistema verifica que la sesion almacenada sigue siendo valida. Si es valida, navega directamente al panel principal. Si no, muestra la pantalla de inicio de sesion.
- **Respuestas 401 del servidor**: Cualquier respuesta de sesion invalida del servidor redirige al inicio de sesion. Si multiples solicitudes simultaneas reciben esta respuesta, solo se redirige una vez.
- **Datos de sesion al cerrar sesion**: Al cerrar sesion se borran todos los datos de sesion almacenados localmente y se invalida la sesion en el servidor.
- **Onboarding unico**: Las pantallas de bienvenida se muestran una sola vez. El estado de completacion se almacena localmente.
- **Contenido general del onboarding**: El contenido del onboarding es general y valido para ambos tipos de contrato (fijo discontinuo e indefinido).
- **Permiso de notificaciones**: Se solicita despues del primer login y antes del onboarding, para vincular el dispositivo al usuario autenticado.
- **Acceso revocado (SAD)**: Si la cuenta de una trabajadora SAD ha sido suspendida, dada de baja o desactivada, al intentar acceder se muestra una pantalla informativa con mensaje claro y datos de contacto de soporte. No se permite navegar a ninguna seccion de la app. No se almacenan datos de sesion.
- **Sin conexion a internet**: Toda accion que requiera comunicacion con el servidor muestra un mensaje de "Sin conexion a internet" y la accion no se completa. No se implementa cola local ni reintento automatico.

### Destinos de navegacion

| Desde | Accion / Condicion | Destino |
|-------|--------------------|---------|
| Splash | Sesion valida | Panel principal |
| Splash | Sesion invalida/no existe | Pantalla de inicio de sesion |
| Login | Cuenta revocada (SAD) | Pantalla de acceso revocado (RF-1.7) |

---

## Criterios de Aceptacion

### CA-001: Splash con logo de marca ← HU-001
GIVEN la trabajadora abre la app
WHEN la app inicia la carga
THEN se muestra la pantalla de splash con el logo de la aplicacion sobre fondo de marca durante un maximo de 3 segundos

### CA-002: Redireccion desde splash segun sesion ← HU-001
GIVEN la pantalla de splash ha finalizado
WHEN el sistema verifica el estado de la sesion
THEN si hay sesion valida, navega al panel principal; si no hay sesion o la sesion es invalida, navega a la pantalla de inicio de sesion

### CA-003: Registro con email y contrasena (Hogar) ← HU-002
GIVEN la trabajadora Hogar esta en la pantalla de registro
WHEN introduce un email valido y una contrasena que cumple los requisitos (minimo 8 caracteres, al menos una mayuscula y un numero)
THEN el sistema completa el registro y la trabajadora queda autenticada automaticamente con sesion activa

### CA-004: Validacion de registro (Hogar) ← HU-002
GIVEN la trabajadora Hogar esta en la pantalla de registro
WHEN introduce un email con formato invalido o una contrasena que no cumple los requisitos
THEN se muestran mensajes de error de validacion en linea indicando el problema especifico

### CA-005: Activacion de cuenta SAD ← HU-004
GIVEN una trabajadora SAD ha recibido un email de activacion desde el backoffice
WHEN abre el enlace del email
THEN puede establecer su contrasena (el email ya esta preconfigurado) y acceder a la app

### CA-006: Inicio de sesion con credenciales ← HU-005
GIVEN la trabajadora esta en la pantalla de inicio de sesion
WHEN introduce email y contrasena validos
THEN el sistema autentica a la trabajadora, establece la sesion y navega al panel principal

### CA-007: Error de credenciales ← HU-005
GIVEN la trabajadora esta en la pantalla de inicio de sesion
WHEN introduce credenciales incorrectas
THEN se muestra un mensaje de error claro indicando que las credenciales no son validas

### CA-008: Bloqueo temporal por intentos fallidos ← HU-005
GIVEN la trabajadora ha introducido credenciales incorrectas N veces consecutivas (N definido por el servidor)
WHEN intenta un nuevo inicio de sesion
THEN el sistema muestra un mensaje indicando que la cuenta esta temporalmente bloqueada y el tiempo de espera restante

### CA-009: Sesion persistente entre usos ← HU-006
GIVEN la trabajadora ha iniciado sesion previamente y no ha cerrado sesion
WHEN abre la app
THEN el sistema verifica la sesion almacenada y, si es valida, navega directamente al panel principal sin mostrar pantalla de login

### CA-010: Redireccion a login por sesion invalida ← HU-006
GIVEN la sesion de la trabajadora ha expirado o ha sido revocada por el servidor
WHEN la app detecta la invalidez de la sesion (al arrancar o en cualquier solicitud al servidor)
THEN redirige a la pantalla de inicio de sesion. Si multiples solicitudes simultaneas detectan sesion invalida, solo se redirige una vez

### CA-011: Flujo de recuperacion de contrasena ← HU-007
GIVEN la trabajadora esta en la pantalla de inicio de sesion
WHEN pulsa "Olvidaste tu contrasena?" o similar
THEN accede a la pantalla de recuperacion con campo de email

### CA-012: Envio de enlace de recuperacion ← HU-007
GIVEN la trabajadora esta en la pantalla de recuperacion
WHEN introduce su email y pulsa enviar
THEN el sistema muestra un mensaje de confirmacion generico (sin revelar si el email existe en el sistema)

### CA-013: Restablecimiento de contrasena ← HU-007
GIVEN la trabajadora ha recibido el email de recuperacion y abre el enlace
WHEN introduce una nueva contrasena que cumple los requisitos de seguridad
THEN la contrasena se restablece y la trabajadora puede iniciar sesion con la nueva contrasena

### CA-014: Enlace de recuperacion caducado ← HU-007
GIVEN la trabajadora abre un enlace de recuperacion que ha expirado
WHEN intenta restablecer la contrasena
THEN el sistema informa que el enlace ya no es valido e invita a solicitar uno nuevo

### CA-015: Cierre de sesion con confirmacion ← HU-008
GIVEN la trabajadora esta autenticada
WHEN pulsa cerrar sesion
THEN se muestra un dialogo de confirmacion. Al confirmar: se borran todos los datos de sesion locales, se invalida la sesion en el servidor y se redirige a la pantalla de inicio de sesion

### CA-016: Pantalla de acceso revocado (SAD) ← HU-009
GIVEN una trabajadora SAD cuya cuenta ha sido suspendida o dada de baja
WHEN intenta acceder a la app
THEN se muestra una pantalla informativa con mensaje "Ya no tienes permisos para acceder a esta aplicacion" e informacion de contacto de soporte. No se permite navegar a ninguna seccion ni se almacenan datos de sesion

---

## Checklist de Validacion

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de exito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [ ] Ambiguedades resueltas — gap P-001 pendiente (contenido onboarding)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegacion enumerados con sus variantes

---

## Fuera de Alcance

- Autenticacion biometrica (Face ID, huella digital): no incluida en esta version.
- Autenticacion de dos factores (2FA): no incluida en esta version.
- Gestion de contrasenas desde la app (cambiar contrasena activa): el cambio de contrasena solo es posible via flujo de recuperacion de acceso.
