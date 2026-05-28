# KMM Skills Architecture

Este directorio contiene las skills reutilizables de KMM organizadas por **dimensión de verdad**. El objetivo es que arquitectura, DI, networking, auth y workflows evolucionen sin contaminarse entre sí.

La estructura está pensada para usarse dentro de una forma de trabajo con agentes más grande:

- un **agente principal** actúa como **orquestador**
- los **subagentes implementadores** contienen y usan estas skills
- el orquestador **no implementa directamente**: analiza, decide, divide el trabajo y delega
- cada subagente decide qué skill aplicar según el problema concreto que le toca resolver

## Modelo de trabajo con agentes

### Papel del agente principal

El agente principal:

- entiende el objetivo global del usuario
- inspecciona el estado del proyecto
- decide qué parte del trabajo corresponde a arquitectura, networking, auth, DI, recursos, etc.
- divide el problema en subtareas coherentes
- delega la implementación a subagentes especializados
- integra y valida el resultado final

El agente principal **no debería usar estas skills como si fuera él quien implementa directamente cada detalle**. Su papel es orquestar.

### Papel de los subagentes

Los subagentes:

- reciben una subtarea concreta
- leen el código del proyecto
- deciden qué skill o skills locales necesitan
- aplican las reglas y workflows correspondientes
- implementan cambios o producen artefactos siguiendo esas skills

Las skills de este directorio viven para ese nivel: **subagentes que implementan**.

### Regla operativa

- El orquestador decide **qué problema resolver** y **a qué subagente delegarlo**.
- El subagente decide **qué skill usar** para resolver su parte.
- Las skills no sustituyen al orquestador.
- Las workflows no sustituyen el diseño de la delegación.

## Principio base de diseño de skills

Cada skill debe poseer solo **una dimensión de verdad**:

- Arquitectura: define capas, ownership y dependencias permitidas
- DI: define cómo se registran y resuelven dependencias
- Networking: separa contrato remoto estable de implementación HTTP
- Auth: separa política de sesión, proveedor OAuth y mecanismo técnico
- Workflows: componen skills, pero no redefinen reglas

## Papel de cada skill

### Arquitectura global

- `kb-kmm-clean-architecture`
  Define la topología global `app / features / core` y las fronteras entre capas.

### Arquitectura por capa

- `kb-kmm-app-layer`
  Define qué pertenece a `app`: composition root, navegación, composición global y wiring de alto nivel.

- `kb-kmm-core-layer`
  Define qué pertenece a `core`: dominio compartido e infraestructura transversal.

- `kb-kmm-app-errors`
  Define el contrato transversal `AppResult` / `AppError`, ownership de taxonomías de error y reglas de adaptación entre capas.

- `kb-kmm-feature-clean-architecture`
  Define la microarquitectura interna de una feature: `presentation / domain / data`.

### DI

- `kb-koin`
  Define el wiring con Koin: módulos, `initKoin`, qualifiers, `nativeModule`, tipos de registro y orden de módulos.

### Storage local

- `kb-kmm-datastore-preferences`
  Define cómo introducir Preferences DataStore en KMM: factory común, path por plataforma, ownership de keys y adapters sobre storage local.

### Recursos y texto

- `kb-kmm-resources`
  Define el sistema de recursos compartidos con `compose.resources`: strings, imágenes, fonts, raw files y localización.

- `kb-kmm-ui-text`
  Define el patrón `UiText` para exponer textos desde ViewModel sin resolverlos fuera de la UI.

### Networking

- `kb-kmm-network-contracts`
  Define el contrato remoto estable sobre el contrato transversal de app: borde remoto, variante `NetworkError`, límite remoto y adaptación a dominio.

- `kb-kmm-http-ktor`
  Define la implementación HTTP concreta con Ktor: `HttpClient`, plugins, logging, timeouts, JSON y helpers Ktor.

### Navegación

- `kb-kmm-navigation-contracts`
  Define el contrato arquitectónico de navegación: ownership en `app`, encapsulación del `NavController`, rutas como contrato central y separación entre features.

- `kb-kmm-navigation-compose`
  Define la implementación concreta con Compose Navigation + Kotlin Serialization: rutas `@Serializable`, `NavHost`, nested graphs, deep links, back stack y shell adaptativo.

- `kb-kmm-navigation-platform-behaviors`
  Define la integración de navegación con el host y la plataforma: `BackHandler`, predictive back y bridges de deep links.

- `kb-kmm-navigation-viewmodel-events`
  Define el patrón de efectos de navegación desde ViewModel: `Channel` vs `StateFlow`, reglas de `LaunchedEffect` y separación entre hecho y destino.

### Variantes y entornos

- `kb-kmm-brands`
  Define la dimensión `brand`: identidad de producto, catálogo de marcas, valores base y separación entre diferencias de marca y diferencias de entorno.

- `kb-kmm-environments`
  Define la semántica estable de `env` y la composición de la matriz `brand × env`: variantes, valores derivados vs declarativos y política de sensibilidad.

- `kb-kmm-android-environments`
  Define la implementación Android del sistema de variantes: flavors, plugin BuildConfig, resolución de variante y `.properties`.

- `kb-kmm-ios-environments`
  Define la implementación iOS del sistema de variantes: `XCConfig`, target/build configuration/scheme y Script Build Phase.

### Auth

- `kb-kmm-auth-contracts`
  Define la política de sesión: tokens, refresh, expiración, endpoints públicos y eventos de sesión.

- `kb-kmm-auth-oauth-keycloak`
  Define el proveedor concreto Keycloak: token endpoint, `realm`, `client_id`, grant types y payloads form-urlencoded.

- `kb-kmm-auth-ktor-plugin`
  Define el mecanismo técnico de auth automática sobre Ktor: plugin, bypass de endpoints públicos, dos clientes y refresh transparente.

### Workflows

- `wf-kmm-datastore-setup`
  Orquesta la configuración de Preferences DataStore respetando capas, providers por plataforma y wiring de DI.

- `wf-kmm-network-setup`
  Orquesta la configuración de networking sin asumir auth concreta.

- `wf-kmm-auth-setup-keycloak`
  Orquesta auth con Keycloak sin asumir por sí sola un mecanismo HTTP concreto.

- `wf-kmm-stack-setup-ktor-keycloak-koin`
  Atajo para el stack habitual Koin + Ktor + Keycloak, componiendo skills ya existentes.

- `wf-kmm-environments`
  Orquesta la configuración del sistema de variantes combinando catálogo de brands, semántica de entornos e implementación Android/iOS.

## Esquema resumido

```text
Arquitectura global
  kb-kmm-clean-architecture

Arquitectura por capa
  kb-kmm-app-layer
  kb-kmm-core-layer
  kb-kmm-app-errors
  kb-kmm-feature-clean-architecture

Brands
  kb-kmm-brands

DI
  kb-koin

Storage local
  kb-kmm-datastore-preferences

Recursos y texto
  kb-kmm-resources
  kb-kmm-ui-text

Networking
  kb-kmm-network-contracts
  kb-kmm-http-ktor

Navegación
  kb-kmm-navigation-contracts
  kb-kmm-navigation-compose
  kb-kmm-navigation-platform-behaviors
  kb-kmm-navigation-viewmodel-events

Auth
  kb-kmm-auth-contracts
  kb-kmm-auth-oauth-keycloak
  kb-kmm-auth-ktor-plugin

Variantes y entornos
  kb-kmm-environments
  kb-kmm-android-environments
  kb-kmm-ios-environments

Workflows
  wf-kmm-datastore-setup
  wf-kmm-network-setup
  wf-kmm-auth-setup-keycloak
  wf-kmm-stack-setup-ktor-keycloak-koin
  wf-kmm-environments
```

## Dirección correcta de dependencias

```text
Arquitectura global y por capa
        ↓
Contratos estables de networking y auth
        ↓
Semántica estable de variantes
        ↓
Implementaciones concretas (Koin, Ktor, Keycloak, plugin auth)
e implementaciones de plataforma para variants
        ↓
Workflows de composición
```

Reglas:

- Las skills de arquitectura y contratos pueden ser consumidas por skills de implementación.
- Las skills de implementación no deben redefinir contratos estables.
- Las workflows pueden componer todas.

## Cómo decidir dónde vive una regla

Antes de escribir una regla, aplicar este filtro:

- Si cambiar Ktor por otra librería HTTP no invalida la regla, no va en `kb-kmm-http-ktor`.
- Si cambiar Koin por otra librería de DI no invalida la regla, no va en `kb-koin`.
- Si cambiar `compose.resources` por otro sistema de recursos invalida la regla, pertenece a `kb-kmm-resources`.
- Si la regla define cómo el ViewModel expone textos a la UI sin resolverlos, pertenece a `kb-kmm-ui-text`.
- Si cambiar Keycloak por otro proveedor no invalida la regla, no va en `kb-kmm-auth-oauth-keycloak`.
- Si cambiar el mecanismo técnico de refresh no invalida la regla, no va en `kb-kmm-auth-ktor-plugin`.
- Si cambiar la organización de capas no invalida la regla, no va en `kb-kmm-clean-architecture`, `kb-kmm-app-layer`, `kb-kmm-core-layer` o `kb-kmm-feature-clean-architecture`.
- Si la regla describe **qué debe pasar**, pertenece a contrato o política.
- Si la regla describe **cómo se hace con una tecnología concreta**, pertenece a implementación.
- Si la regla describe **cómo se combinan varias skills**, pertenece a una workflow.

## Cuándo crear una skill nueva

Crear una skill nueva cuando aparezca una variante estable que merezca aislarse:

- nueva librería HTTP
- nueva librería de DI
- nuevo proveedor OAuth
- nueva estrategia técnica de auth
- nueva convención arquitectónica compartida por muchos proyectos

No crear una skill nueva si solo estás añadiendo un detalle menor a una responsabilidad ya existente.

## Global vs proyecto

### Skill global

Debe vivir aquí cuando representa un patrón reutilizable en muchos proyectos:

- arquitectura KMM base
- Koin
- Ktor
- contratos de networking
- contratos de auth
- Keycloak si es proveedor frecuente
- plugin Ktor de auth si es estrategia recurrente

### Skill local de proyecto

Debe vivir en el repo concreto cuando el proyecto se sale de la convención global:

- otra organización de capas
- otra DI
- otro proveedor OAuth
- otra estrategia de auth
- restricciones específicas de backend, despliegue o plataforma

## Objetivo de esta estructura

Esta separación permite cambios acotados:

- cambiar Ktor sin tocar contratos de red o auth
- cambiar Koin sin tocar arquitectura ni políticas
- cambiar Keycloak sin tocar la política general de sesión
- cambiar el mecanismo de refresh sin tocar el contrato de auth
- cambiar la arquitectura por capas sin reescribir skills de DI, HTTP o proveedor OAuth

## Recomendación operativa

Cuando evoluciones estas skills:

1. Añade primero la regla a arquitectura o contrato si es estable.
2. Añade después la implementación concreta solo en la skill tecnológica afectada.
3. Ajusta workflows solo para orquestar, no para redefinir reglas.
4. Mantén los aliases heredados congelados.
5. Piensa siempre en dos niveles:
   el orquestador decide la delegación;
   el subagente decide qué skill aplicar para implementar.
