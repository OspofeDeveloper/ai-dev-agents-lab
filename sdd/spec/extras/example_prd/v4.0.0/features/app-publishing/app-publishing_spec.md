# Spec: App Publishing
> Versión: 1.0 | Fecha: 2026-04-05
> Generado via: fast-track desde prd-hogar-sad.md (scope: F-012 via prd-hogar-sad_discovery.md)
> Feature ID: F-012
> Spec monolítico origen: N/A (features-first via discover)

---

## Actores

| Actor | Descripción | Capacidades en esta feature |
|-------|-------------|----------------------------|
| Equipo de desarrollo / DevOps | Responsable de la configuración de builds, preparación de metadatos y publicación en tiendas | Configurar flavors/targets de build, preparar metadatos de store, someter apps a revisión en ambas tiendas, gestionar cumplimiento normativo |

---

## Historias de Usuario

### HU-001: Compilar dos apps de marca desde codebase compartido
Como equipo de desarrollo,
quiero compilar dos aplicaciones independientes (CUIDEO Hogar y Felizvita SAD) desde el mismo codebase compartido con branding diferenciado,
para que cada perfil de trabajadora tenga una app propia con identidad visual y funcionalidades exclusivas de su perfil.

### HU-002: Publicar las apps en App Store
Como equipo de desarrollo,
quiero preparar y publicar la aplicación CUIDEO y la aplicación Felizvita en la App Store de Apple,
para que las trabajadoras con dispositivos iOS puedan descargarlas desde la tienda oficial.

### HU-003: Publicar las apps en Google Play
Como equipo de desarrollo,
quiero preparar y publicar la aplicación CUIDEO y la aplicación Felizvita en Google Play Store,
para que las trabajadoras con dispositivos Android puedan descargarlas desde la tienda oficial.

### HU-004: Cumplir con los requisitos normativos de las tiendas
Como equipo de desarrollo,
quiero documentar y declarar el cumplimiento normativo (RGPD, privacidad de datos, permisos, SDKs de terceros) exigido por las tiendas,
para que las apps superen la revisión de las tiendas y operen legalmente en la Unión Europea.

---

## Recorridos de Usuario

### Journey 1: Configurar y compilar las dos apps de marca
Actor: Equipo de desarrollo | Objetivo: Obtener dos builds diferenciados desde el codebase compartido

1. El equipo define los flavors/targets de build en el proyecto: uno para CUIDEO (perfil Hogar) y otro para Felizvita (perfil SAD).
2. Cada flavor/target lleva asociados su propio nombre de app, identificador de aplicación, icono y color primario de marca.
3. El equipo compila el flavor CUIDEO: el resultado es una app que muestra únicamente las funcionalidades del perfil Hogar y adopta la identidad visual azul de CUIDEO.
4. El equipo compila el flavor Felizvita: el resultado es una app que muestra únicamente las funcionalidades del perfil SAD y adopta la identidad visual verde de Felizvita.
5. Ambas apps son compiladas en sus formatos de distribución (IPA para iOS, APK/AAB para Android) listas para subida a las tiendas.

Estado de éxito: Existen dos binarios separados, verificables y distintos — uno identificado como CUIDEO Hogar y otro como Felizvita SAD — que no comparten funcionalidades entre perfiles.
Flujos alternativos: Si el codebase compartido no permite aislar completamente las funcionalidades por perfil → la compilación no es válida hasta que la separación sea completa.

---

### Journey 2: Preparar y publicar en la App Store de Apple
Actor: Equipo de desarrollo | Objetivo: Que ambas apps estén disponibles para descarga en iOS

1. El equipo accede a su cuenta de App Store Connect y configura los registros de app para CUIDEO Hogar y Felizvita SAD.
2. Para cada app prepara los metadatos requeridos: nombre, descripción, capturas de pantalla, URL de política de privacidad y URL de soporte.
3. El equipo asigna la categoría de la aplicación y la clasificación por edades correspondiente.
4. Se sube el binario IPA correspondiente a cada app.
5. El equipo envía cada app a revisión de Apple.
6. Una vez aprobadas, las apps quedan disponibles en la App Store para descarga pública.

Estado de éxito: Tanto CUIDEO como Felizvita están visibles y descargables en la App Store para dispositivos iOS compatibles.
Flujos alternativos: Si Apple rechaza la revisión → el equipo atiende los motivos indicados, realiza las correcciones y vuelve a someter la app a revisión.

---

### Journey 3: Preparar y publicar en Google Play Store
Actor: Equipo de desarrollo | Objetivo: Que ambas apps estén disponibles para descarga en Android

1. El equipo accede a su cuenta de Google Play Console y crea las fichas de CUIDEO Hogar y Felizvita SAD.
2. Para cada app prepara los metadatos requeridos: nombre, descripción breve, descripción completa, capturas de pantalla, imagen destacada, URL de política de privacidad.
3. El equipo completa el cuestionario de clasificación de contenido y asigna la categoría de la app.
4. Se sube el binario AAB/APK de cada app.
5. El equipo envía cada app a revisión de Google.
6. Una vez aprobadas, las apps quedan disponibles en Google Play para descarga pública.

Estado de éxito: Tanto CUIDEO como Felizvita están visibles y descargables en Google Play para dispositivos Android compatibles.
Flujos alternativos: Si Google rechaza la revisión → el equipo atiende los motivos indicados, realiza las correcciones y vuelve a someter la app a revisión.

---

### Journey 4: Preparar documentación de cumplimiento normativo
Actor: Equipo de desarrollo | Objetivo: Cumplir con los requisitos normativos de las tiendas y la legislación vigente

1. El equipo redacta la documentación de cumplimiento del RGPD que declara qué datos personales recoge cada app, con qué finalidad y qué base legal.
2. El equipo justifica formalmente el uso de cada permiso sensible que solicita la app (acceso a ubicación, notificaciones push).
3. El equipo declara los SDKs de análisis y mensajería de terceros utilizados en ambas apps, de acuerdo con los formularios requeridos por cada tienda.
4. La política de privacidad publicada en una URL accesible cubre ambas apps.
5. Esta documentación se asocia a cada ficha de app en las tiendas antes de la primera publicación.

Estado de éxito: Las apps superan los controles de privacidad de App Store y Google Play; la política de privacidad está publicada y enlazada en ambas fichas.
Flujos alternativos: Si las tiendas detectan inconsistencias en las declaraciones de privacidad → el equipo corrige la documentación y la ficha, y vuelve a someter la app.

---

## Resultados y Éxito

La feature `app-publishing` se considera completada cuando:

1. Existen dos apps compiladas y diferenciadas: **CUIDEO** (perfil Hogar, identidad visual azul) y **Felizvita** (perfil SAD, identidad visual verde), cada una con su nombre de app e identificador de aplicación propio.
2. Ambas apps están publicadas y disponibles para descarga pública en la App Store de Apple para dispositivos iOS 16 o superior.
3. Ambas apps están publicadas y disponibles para descarga pública en Google Play Store para dispositivos Android 8.0 o superior.
4. Cada ficha de app en ambas tiendas cuenta con metadatos completos: nombre, descripción, capturas de pantalla, clasificación de edades, categoría, URL de política de privacidad y URL de soporte.
5. Las apps han superado la revisión de cumplimiento normativo de ambas tiendas, con declaraciones de RGPD, permisos de ubicación y SDKs de terceros debidamente justificadas.

---

## Instrucciones Inambiguas

### Reglas de comportamiento

**Sobre la separación por perfil:**
- La app CUIDEO muestra exclusivamente las funcionalidades del perfil Hogar; no expone ninguna pantalla, sección ni flujo del perfil SAD.
- La app Felizvita muestra exclusivamente las funcionalidades del perfil SAD; no expone ninguna pantalla, sección ni flujo del perfil Hogar.
- Ambas apps son compiladas desde el mismo codebase compartido; la separación se logra mediante configuración de build, no mediante dos codebases distintos.

**Sobre la identidad visual:**
- CUIDEO tiene color primario de marca azul y un icono de app temático azul.
- Felizvita tiene color primario de marca verde y un icono de app temático verde.
- Los valores exactos de los colores de marca serán confirmados por el cliente; mientras tanto se aplican los tonos definidos en el discovery (azul para CUIDEO, verde para Felizvita). Ver Asunciones Aplicadas [A-001].

**Sobre los identificadores de aplicación:**
- CUIDEO Hogar tiene un identificador de aplicación propio en iOS y en Android.
- Felizvita SAD tiene un identificador de aplicación propio, distinto del de CUIDEO, en iOS y en Android.
- Los identificadores deben ser únicos y permanecer estables tras el lanzamiento; un cambio de identificador implica tratar la app como una app nueva en las tiendas.

**Sobre los metadatos de store:**
- Ambas apps requieren metadatos completos en ambas tiendas antes de la primera publicación.
- Los metadatos incluyen obligatoriamente: nombre, descripción, capturas de pantalla representativas, clasificación de edades, categoría, URL de política de privacidad y URL de soporte.
- Las capturas de pantalla deben ser representativas del flujo real de la app y estar en los tamaños requeridos por cada tienda en el momento de la publicación.

**Sobre las pruebas beta:**
- Las pruebas beta mediante TestFlight (iOS) o pistas de pruebas de Google Play son opcionales para el MVP. Su realización no bloquea la publicación. Ver Asunciones Aplicadas [A-002].

**Sobre los metadatos en idiomas:**
- Para el MVP, los metadatos de ambas tiendas se preparan únicamente en español. Ver Asunciones Aplicadas [A-003].

**Sobre el cumplimiento normativo:**
- El cumplimiento normativo no es opcional; su documentación debe estar completa antes de someter las apps a revisión en las tiendas.
- La política de privacidad debe estar publicada en una URL activa y accesible públicamente en el momento de la revisión.
- Los permisos de ubicación deben ir acompañados de una justificación funcional clara: se usan para verificar la presencia de la trabajadora en el lugar de prestación del servicio en el momento del fichaje.
- Los SDKs de terceros relevantes para la declaración de privacidad incluyen al menos los de mensajería y análisis utilizados en ambas apps.

### Destinos de navegación

Esta feature no genera flujos de navegación en la app. Es una feature de configuración, compilación y publicación gestionada íntegramente por el equipo técnico fuera de la experiencia de usuario de la app.

---

## Criterios de Aceptación

### CA-001: App CUIDEO compila con identidad Hogar exclusiva ← HU-001
GIVEN que el codebase compartido está configurado con el flavor/target de CUIDEO Hogar
WHEN se compila el binario de distribución de CUIDEO
THEN el binario resultante muestra el nombre "CUIDEO", el icono de app azul, el color primario azul de la marca y contiene exclusivamente las funcionalidades del perfil Hogar, sin exponer ningún flujo ni pantalla del perfil SAD

### CA-002: App Felizvita compila con identidad SAD exclusiva ← HU-001
GIVEN que el codebase compartido está configurado con el flavor/target de Felizvita SAD
WHEN se compila el binario de distribución de Felizvita
THEN el binario resultante muestra el nombre "Felizvita", el icono de app verde, el color primario verde de la marca y contiene exclusivamente las funcionalidades del perfil SAD, sin exponer ningún flujo ni pantalla del perfil Hogar

### CA-003: Identificadores de app son únicos y diferenciados ← HU-001
GIVEN que ambos flavors/targets están configurados
WHEN se verifican los identificadores de aplicación de CUIDEO y Felizvita
THEN CUIDEO tiene un identificador de aplicación propio en iOS y en Android, y Felizvita tiene un identificador de aplicación distinto en iOS y en Android; ambos identificadores son únicos entre sí

### CA-004: CUIDEO publicada y descargable en App Store ← HU-002
GIVEN que la app CUIDEO tiene metadatos completos y el binario IPA ha superado la revisión de Apple
WHEN un usuario con dispositivo iOS 16 o superior busca "CUIDEO" en la App Store
THEN la ficha de la app aparece en los resultados y la app puede descargarse e instalarse sin errores en el dispositivo

### CA-005: Felizvita publicada y descargable en App Store ← HU-002
GIVEN que la app Felizvita tiene metadatos completos y el binario IPA ha superado la revisión de Apple
WHEN un usuario con dispositivo iOS 16 o superior busca "Felizvita" en la App Store
THEN la ficha de la app aparece en los resultados y la app puede descargarse e instalarse sin errores en el dispositivo

### CA-006: CUIDEO publicada y descargable en Google Play ← HU-003
GIVEN que la app CUIDEO tiene metadatos completos y el binario AAB ha superado la revisión de Google
WHEN un usuario con dispositivo Android 8.0 o superior busca "CUIDEO" en Google Play
THEN la ficha de la app aparece en los resultados y la app puede descargarse e instalarse sin errores en el dispositivo

### CA-007: Felizvita publicada y descargable en Google Play ← HU-003
GIVEN que la app Felizvita tiene metadatos completos y el binario AAB ha superado la revisión de Google
WHEN un usuario con dispositivo Android 8.0 o superior busca "Felizvita" en Google Play
THEN la ficha de la app aparece en los resultados y la app puede descargarse e instalarse sin errores en el dispositivo

### CA-008: Metadatos de store completos para ambas apps en ambas tiendas ← HU-002, HU-003
GIVEN que se está preparando la publicación de cualquiera de las dos apps en cualquiera de las dos tiendas
WHEN se revisa la ficha de la app antes de someter a revisión
THEN la ficha contiene: nombre, descripción, al menos tres capturas de pantalla representativas, clasificación de edades, categoría asignada, URL de política de privacidad activa y URL de soporte activa

### CA-009: Política de privacidad publicada y enlazada ← HU-004
GIVEN que se va a someter cualquiera de las apps a revisión en cualquiera de las tiendas
WHEN las tiendas verifican el enlace de política de privacidad en la ficha
THEN la URL de política de privacidad apunta a un documento públicamente accesible, activo y que cubre el tratamiento de datos de ambas apps

### CA-010: Declaración de permisos de ubicación con justificación funcional ← HU-004
GIVEN que ambas apps solicitan permiso de acceso a la ubicación del dispositivo
WHEN las tiendas revisan las justificaciones de permisos
THEN la justificación del permiso de ubicación declara que su uso es para verificar la presencia de la trabajadora en el lugar de prestación del servicio en el momento del registro horario, y esta justificación es aceptada por la revisión de la tienda

### CA-011: Declaración de SDKs de terceros completa ← HU-004
GIVEN que ambas apps integran SDKs de terceros para mensajería y análisis
WHEN las tiendas requieren la declaración de SDKs de terceros
THEN se ha completado el formulario de declaración correspondiente en cada tienda, listando todos los SDKs relevantes y su finalidad, y las apps superan el control de privacidad de la tienda

### CA-012: Versiones iOS mínima compatible verificada ← HU-002
GIVEN que ambas apps están configuradas para sus respectivos flavors/targets
WHEN se compila y verifica la compatibilidad mínima de iOS
THEN la app declara soporte para iOS 16 como versión mínima y no puede instalarse en versiones anteriores

### CA-013: Versión Android mínima compatible verificada ← HU-003
GIVEN que ambas apps están configuradas para sus respectivos flavors/targets
WHEN se compila y verifica la compatibilidad mínima de Android
THEN la app declara soporte para Android 8.0 (API Level 26) como versión mínima y no puede instalarse en versiones anteriores

---

## Checklist de Validación

- [x] Actores identificados
- [x] Flujos principales descritos paso a paso
- [x] Estados de éxito definidos para cada journey
- [x] Edge cases documentados (rechazo de revisión de tiendas)
- [x] Estados de error definidos (compilación no válida si perfiles no están aislados)
- [x] Ambigüedades resueltas (colores, beta testing, idiomas de metadatos — con asunciones)
- [x] Cada CA referencia su HU padre
- [x] Cada CA es testable de forma independiente
- [x] Destinos de navegación enumerados (no aplica: feature sin UI de usuario final)

---

## Fuera de Alcance

- **Automatización del pipeline de CI/CD**: la configuración de pipelines de integración y entrega continua para compilación y despliegue automático no forma parte de este spec; si se requiere, es materia del Plan técnico.
- **Actualizaciones y versionado posterior al MVP**: la gestión de versiones futuras, hotfixes y el proceso de actualización en tiendas tras el lanzamiento inicial no está cubierta en este spec.
- **Pruebas beta obligatorias**: TestFlight y pistas de pruebas cerradas de Google Play son opcionales; este spec no cubre el proceso de gestión de testers ni feedback beta.
- **Localización a otros idiomas**: los metadatos de las tiendas se preparan en español para el MVP; la localización a otros idiomas queda fuera de este spec.
- **Cumplimiento normativo de mercados fuera de la Unión Europea**: este spec cubre únicamente el cumplimiento RGPD aplicable al mercado europeo.
- **Diseño visual detallado**: los valores exactos de colores de marca, tipografías y guías de estilo son responsabilidad del equipo de diseño y se definen fuera de este spec (ver [A-001]).
- **Gestión de cuentas de developer**: la creación y gestión de las cuentas de App Store Connect y Google Play Console no forma parte de este spec; se asume que las cuentas existen o serán gestionadas por el cliente.

---

## Asunciones Aplicadas

- **[A-001]**: Los colores exactos de marca de cada app (CUIDEO azul, Felizvita verde) están pendientes de confirmación definitiva por el cliente. Se asume que los tonos indicados en el PRD son orientativos. El spec define el color como "azul" y "verde" sin especificar valores exactos; los valores hex definitivos se resolverán en el Plan técnico o en una instrucción específica del cliente. Impacto: los CAs de identidad visual se verifican por tono de color, no por valor hex exacto.
- **[A-002]**: Las pruebas beta (TestFlight / pistas cerradas de Google Play) se tratan como opcionales para el MVP. Si el cliente decide que son obligatorias, este spec deberá actualizarse y los journeys de beta testing deberán documentarse. No bloquean la publicación.
- **[A-003]**: Los metadatos de ambas tiendas (descripción, capturas, etc.) se preparan únicamente en español para el lanzamiento MVP. Si se requiere localización a otros idiomas, es una extensión fuera de alcance de este spec.
