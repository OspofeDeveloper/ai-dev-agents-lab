---
name: kb-kmm-environments
description: "Base de conocimiento de entornos y variantes en proyectos KMM: semántica estable de env, composición de la matriz brand×env, valores derivados vs declarativos, fuentes de verdad por plataforma y criterios para configuración sensible."
argument-hint: ""
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KMM Environments — Base de Conocimiento

## Regla 1: `env` es una dimensión distinta de `brand`

El sistema de variantes combina dos ejes conceptualmente separados:

| Dimensión | Controla |
|-----------|----------|
| `env` | destino de integración, URLs, sufijos de build, flags de entorno y cualquier configuración dependiente del entorno |

La semántica de `brand` vive en `kb-kmm-brands`.

Esta skill se centra en `env` y en cómo `env` se combina con el catálogo de brands para formar variantes.

---

## Regla 2: La matriz de variantes compone brands y entornos

Antes de hablar de Gradle, XCConfig o cualquier tooling, el proyecto debe poder expresar con claridad:

- qué entornos existen
- qué combinación genera cada variante
- qué valores son propios de una variante concreta

La matriz `brand × env` se construye combinando:

- el catálogo de brands definido en `kb-kmm-brands`
- el catálogo de entornos definido por esta skill

Android e iOS solo materializan esa matriz con mecanismos distintos.

---

## Regla 3: Los valores de entorno son los que cambian por destino operativo

`env` agrupa diferencias como:

- URL base o destino de integración
- sufijos de build
- flags de entorno
- configuración externa que cambia entre pre, pro, staging, qa o equivalentes

Si un valor permanece estable al cambiar solo el entorno, no pertenece a `env`.

---

## Regla 4: Distinguir valores declarativos de valores derivados

No toda variable de configuración debe declararse explícitamente por variante.

- **Declarativos**: valores que no se pueden derivar con seguridad de `brand` y `env` como URLs, keys, identificadores externos o flags arbitrarios
- **Derivados**: valores que el sistema puede calcular de forma determinista a partir de `brand` y `env`

El sistema de tooling no debe obligar a persistir manualmente valores derivados si ya puede calcularlos de forma estable.

---

## Regla 5: El código compartido consume un único contrato de configuración

El proyecto expone un único objeto o contrato de configuración accesible desde `commonMain`.

Ese contrato debe reflejar la variante activa en tiempo de compilación o resolución, independientemente de si la plataforma materializa esa variante con:

- Gradle properties
- product flavors
- BuildConfig
- XCConfig
- scripts de build

La semántica compartida es estable aunque cambie el mecanismo concreto.

---

## Regla 6: Cada plataforma tiene su propia fuente de verdad operativa

La semántica de variante es única, pero cada plataforma puede tener una fuente operativa distinta:

- Android puede resolver la variante desde propiedades explícitas, tareas o flavors
- iOS puede resolverla desde target, build configuration, scheme y/o XCConfig

La regla importante no es que ambas plataformas funcionen igual, sino que ambas resuelvan la misma matriz conceptual de variantes.

---

## Regla 7: La configuración sensible sigue una política distinta a la configuración pública

No todos los valores de variante tienen el mismo tratamiento:

- valores públicos o no sensibles pueden vivir versionados
- secretos o credenciales no deben commitearse
- el sistema debe permitir que CI o el entorno de build inyecten esos valores sin romper la matriz de variantes

La política de sensibilidad forma parte del diseño del sistema, no del tooling concreto.

---

## Regla 8: La implementación Android y la implementación iOS viven en skills separadas

Esta skill solo define la semántica estable del sistema multi-brand/multi-environment.

Las decisiones concretas de implementación viven en:

- `kb-kmm-android-environments`
- `kb-kmm-ios-environments`

No duplicar aquí reglas propias de:

- plugins Gradle concretos
- `BuildConfig`
- `XCConfig`
- scripts de Xcode
- target/build configuration/scheme

---

## Regla 9: Los workflows componen brands, entornos y tooling

Las workflows pueden usar esta skill para:

- consumir el catálogo de brands definido en `kb-kmm-brands`
- construir la matriz de variantes
- decidir qué es derivado y qué es declarativo
- validar qué valores son sensibles

Pero la implementación operativa se delega a las skills de Android e iOS, no se redefine aquí.
