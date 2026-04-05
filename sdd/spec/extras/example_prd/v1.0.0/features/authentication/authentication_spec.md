# Spec: Authentication
> Versión: 1.1 | Fecha: 2026-04-05
> Spec monolítico origen: prd-hogar-sad_spec.md
> Feature ID: F-001

---

## Actores
| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Trabajadora Hogar | Trabajadora de cuidado a domicilio con contrato fijo discontinuo que busca oportunidades. Usa la app CUIDEO (identidad visual azul). | Registro, login, onboarding, recuperar contraseña, cerrar sesión. |
| Trabajadora SAD | Trabajadora contratada del Servicio de Asistencia Social que gestiona servicios asignados. Usa la app Felizvita (identidad visual verde). | Login, onboarding, cerrar sesión, ver pantalla de acceso revocado. |
| Sistema / Backoffice | Equipo de coordinación y administración que gestiona el backend y los datos. | Crear cuentas SAD, revocar acceso a trabajadoras. No es un actor de la app móvil pero sus acciones generan estados visibles para las trabajadoras. |

---

## Historias de Usuario

### HU-001: Ver la pantalla de splash al abrir la app
Como trabajadora (Hogar o SAD) / quiero ver una pantalla de bienvenida con el logo de la app al abrirla / para que la app se identifique visualmente antes de redirigirme al flujo de acceso.

### HU-002: Completar el onboarding inicial
Como trabajadora (Hogar o SAD) / quiero ver un onboarding con las funcionalidades principales de la app la primera vez que accedo / para que pueda entender qué puedo hacer con la app antes de usarla.

### HU-003: Iniciar sesión en la app
Como trabajadora (Hogar o SAD) / quiero iniciar sesión con mi email y contraseña / para que pueda acceder a la app de forma segura y mantener mi sesión activa sin necesidad de volver a hacer login en cada acceso.

### HU-004: Registrarme en la app (Hogar)
Como trabajadora Hogar / quiero registrarme en la app introduciendo mi email y contraseña / para que pueda crear mi cuenta y empezar a usar la app.

### HU-005: Cerrar sesión
Como trabajadora (Hogar o SAD) / quiero cerrar sesión de forma explícita / para que mis datos queden protegidos si comparto o pierdo el dispositivo.

### HU-006: Ver pantalla de acceso revocado (SAD)
Como trabajadora SAD cuya cuenta ha sido suspendida o dada de baja / quiero ver una pantalla informativa en lugar de acceder a la app / para que entienda que ya no tengo acceso y sepa a dónde dirigirme.

### HU-007: Recuperar el acceso a mi cuenta
Como trabajadora (Hogar o SAD) / quiero recuperar el acceso a mi cuenta si olvido mi contraseña / para que pueda volver a usar la app sin necesidad de contactar con soporte.

---

## Recorridos de Usuario

### Journey 1: Primera apertura y onboarding
Actor: Trabajadora Hogar o SAD | Objetivo: Llegar a la pantalla principal tras instalar la app

1. La trabajadora abre la app por primera vez.
2. La app muestra la pantalla de splash con el logo de la marca durante 2-3 segundos.
3. No hay sesión activa; la app redirige al login.
4. La trabajadora inicia sesión con email y contraseña (Hogar: credenciales creadas en el registro; SAD: credenciales creadas externamente por el backoffice).
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

### Journey 3: Primer acceso de trabajadora SAD
Actor: Trabajadora SAD | Objetivo: Acceder a la app por primera vez con las credenciales creadas por el backoffice

1. El backoffice crea la cuenta de la trabajadora SAD de forma externa y le comunica las credenciales.
2. La trabajadora abre la app e introduce su email y contraseña en la pantalla de login.
3. Tras el login exitoso, la app solicita permiso de notificaciones push.
4. La app muestra las pantallas de onboarding (primera vez).
5. La app solicita permiso de ubicación con explicación del uso para fichaje.
6. El onboarding finaliza y la trabajadora llega a la home del perfil SAD.

Estado de éxito: La trabajadora SAD accede a su home personalizada tras iniciar sesión con las credenciales creadas externamente.

Flujos alternativos:
- Si la trabajadora introduce credenciales incorrectas → se muestra un mensaje de error genérico.

---

## Resultados y Éxito

- **Autenticación completada**: La trabajadora llega a su home personalizada sin ver pantallas de login en aperturas posteriores hasta que la sesión expire (30 días de inactividad) o cierre sesión explícitamente.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Sesión y autenticación:**
- La sesión se mantiene activa durante 30 días desde el último uso. Expira si la trabajadora lleva 30 días sin acceder, cierra sesión explícitamente, o su cuenta es revocada por administración.
- Las credenciales de sesión se almacenan en el área de seguridad del dispositivo, protegidas contra acceso no autorizado por otras aplicaciones.
- Toda la comunicación de la app con el servidor está cifrada y protegida contra interceptación.
- Al detectar sesión inválida durante múltiples operaciones simultáneas: mostrar el login una única vez, cancelar las operaciones pendientes, no mostrar múltiples diálogos de error.
- Cualquier error en el inicio de sesión (credenciales incorrectas, cuenta bloqueada temporalmente por intentos fallidos, u otro error) muestra siempre un mensaje genérico de error ("Ha habido un error en el inicio de sesión"). Por motivos de seguridad, el mensaje de error de login no debe revelar la causa específica del fallo.

**Cuentas SAD:**
- Las cuentas de las trabajadoras SAD se crean de forma externa desde el backoffice. La app no ofrece registro de cuentas para el perfil SAD. Las trabajadoras SAD acceden a la app únicamente mediante login con las credenciales creadas externamente.

**Perfiles diferenciados:**
- El producto se presenta como dos aplicaciones de marca diferenciada (CUIDEO para perfil Hogar con identidad visual azul, Felizvita para perfil SAD con identidad visual verde) que comparten las mismas funcionalidades de base y adaptan su contenido al tipo de contrato de la trabajadora.
- Los colores exactos de marca serán provistos por el cliente en las guías de marca.

**Experiencia general:**
- Toda acción del usuario produce confirmación visual inmediata. Las operaciones que requieren tiempo de espera muestran un indicador de progreso hasta completarse.
- La app puede mostrarse en múltiples idiomas. El lanzamiento inicial es en castellano; la estructura permite añadir catalán, inglés y francés en versiones futuras.

### Destinos de navegación
| Desde | Acción / Condición | Destino |
|-------|--------------------|---------|
| Splash | Hay sesión válida al abrir | Home (según perfil) |
| Splash | No hay sesión válida | Login |
| Login | Login exitoso | Solicitud permiso notificaciones push → Onboarding (solo primera vez) → Home |
| Login | Login exitoso (no primera vez) | Home (según perfil) |
| Login | Cuenta suspendida / revocada (SAD) | Pantalla de acceso revocado |
| Login | Error de inicio de sesión (cualquier causa) | Permanece en Login con mensaje genérico de error |

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

### CA-008: Login con error — mensaje genérico ← HU-003
GIVEN la trabajadora introduce email o contraseña incorrectos, o su cuenta está bloqueada temporalmente por intentos fallidos, o se produce cualquier otro error en el inicio de sesión
WHEN pulsa "Iniciar sesión"
THEN la app muestra un mensaje genérico de error ("Ha habido un error en el inicio de sesión") sin revelar la causa específica del fallo; no redirige a la home.

---

### CA-009: Validación de formato de email en login ← HU-003
GIVEN la trabajadora está en la pantalla de login
WHEN introduce un email con formato inválido y pulsa "Iniciar sesión"
THEN la app muestra un error de validación en el campo email antes de enviar la solicitud al servidor.

---

### CA-010: Bloqueo temporal por intentos fallidos — mensaje genérico ← HU-003
GIVEN la trabajadora ha fallado múltiples intentos de login consecutivos y el sistema aplica un bloqueo temporal
WHEN intenta iniciar sesión una vez más
THEN la app muestra el mismo mensaje genérico de error ("Ha habido un error en el inicio de sesión") sin indicar que la cuenta está bloqueada, sin revelar la duración del bloqueo ni ofrecer mecanismos de desbloqueo diferenciados; el comportamiento es indistinguible del error por credenciales incorrectas.

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

### CA-014: Registro Hogar — campos y validaciones ← HU-004
GIVEN la trabajadora Hogar está en la pantalla de registro
WHEN introduce su email y contraseña
THEN la app valida el formato del email y que la contraseña cumple los requisitos (mínimo 8 caracteres, al menos una mayúscula y un número) antes de enviar el formulario.

---

### CA-015: Registro Hogar — alta completada ← HU-004
GIVEN la trabajadora Hogar ha introducido datos válidos en el formulario de registro
WHEN pulsa "Registrarse"
THEN el alta se completa y la trabajadora inicia sesión directamente, llegando a su home.

---

### CA-016: Registro Hogar — errores de validación ← HU-004
GIVEN la trabajadora Hogar introduce datos con formato inválido en el registro
WHEN pulsa "Registrarse"
THEN la app muestra mensajes de error claros en los campos con problemas, sin enviar el formulario.

---

### CA-017: Cerrar sesión — confirmación y limpieza ← HU-005
GIVEN la trabajadora accede a la opción de cerrar sesión
WHEN pulsa "Cerrar sesión"
THEN se muestra un diálogo de confirmación; al confirmar, se borran todos los tokens y datos de sesión almacenados en el dispositivo, se invalida el token en el backend y se redirige a la pantalla de login.

---

### CA-018: Acceso revocado — pantalla informativa (SAD) ← HU-006
GIVEN una trabajadora SAD intenta acceder con credenciales válidas pero su cuenta ha sido suspendida, dada de baja o desactivada
WHEN el backend devuelve el estado de cuenta revocada durante la autenticación
THEN se muestra la pantalla de acceso revocado con el mensaje "Ya no tienes permisos para acceder a esta aplicación", información de contacto o soporte, y sin posibilidad de navegar a ninguna sección de la app; no se almacenan tokens en este estado.

---

### CA-019: Recuperar contraseña — flujo completo ← HU-007
GIVEN la trabajadora pulsa "¿Olvidaste tu contraseña?" en el login
WHEN introduce su email en la pantalla de recuperación
THEN la app muestra confirmación del envío del email sin revelar si el email existe en el sistema; el enlace recibido permite establecer una nueva contraseña que cumple los mismos requisitos que el registro (mínimo 8 caracteres, al menos una mayúscula y un número); si la cuenta está dada de baja, el enlace muestra la pantalla de acceso revocado.

---

## Checklist de Validación
- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de éxito definidos
- [x] Edge cases documentados
- [x] Estados de error definidos
- [x] Ambigüedades resueltas
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados con sus variantes

---

## Fuera de Alcance
- Autenticación biométrica (Face ID, huella digital)
- Autenticación de dos factores (2FA)
- Registro de cuentas SAD dentro de la app (las cuentas SAD se crean exclusivamente desde el backoffice)

---

## Changelog

### v1.1 — 2026-04-05
- **Completadas**: HU-003 "Iniciar sesión en la app" (gap [P-001] resuelto)
- **Eliminadas**: HU-004 "Activar mi cuenta (SAD)" (gap [P-007] resuelto — el cliente confirma que no existe flujo de activación en la app; las cuentas SAD se crean externamente y la trabajadora accede mediante login)
- **Eliminadas**: CA-014 "Activación de cuenta SAD — flujo pendiente" (asociado a HU-004 eliminada)
- **Modificadas**: CA-008 "Login con credenciales incorrectas" → ahora "Login con error — mensaje genérico" — unificado con comportamiento de bloqueo: siempre mensaje genérico por seguridad
- **Completadas**: CA-010 "Bloqueo temporal por intentos fallidos" (gap [P-001] resuelto — mensaje genérico indistinguible de otros errores de login)
- **CAs nuevos**: ninguno
- **Modificadas**: Journey 3 "Activación de cuenta por primera vez (SAD)" → ahora "Primer acceso de trabajadora SAD" — refleja que la cuenta ya existe y la trabajadora simplemente inicia sesión
- **Reglas**: nueva "Cuentas SAD" — las cuentas se crean externamente, no hay registro SAD en la app
- **Reglas**: nueva regla de mensaje genérico de error en login por seguridad
- **Renumeración**: HUs renumeradas (antigua HU-005→HU-004, HU-029→HU-005, HU-032→HU-006, HU-035→HU-007); CAs renumerados (CA-015→CA-014 a CA-020→CA-019)
- **Fuera de Alcance**: añadido "Registro de cuentas SAD dentro de la app"
