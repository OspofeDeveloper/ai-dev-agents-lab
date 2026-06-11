---
name: kb-kmm-brands
description: "Brands en proyectos KMM: identidad de producto por marca, catálogo de brands, valores base por marca, assets/naming/bundle id base y separación entre diferencias de marca y diferencias de entorno."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KMM Brands — Base de Conocimiento

## Regla 1: `brand` es una dimensión de identidad de producto

Una `brand` representa una identidad de producto dentro de la misma base técnica.

Una brand puede definir:

- nombre de producto
- identidad visual y assets
- bundle ID o application ID base
- textos o recursos específicos
- composición funcional o routing dependiente de marca

No define por sí sola el destino de integración ni el entorno operativo de despliegue. Eso pertenece a `env`.

---

## Regla 2: El catálogo de brands es una fuente de verdad estable

El proyecto debe poder expresar con claridad:

- qué brands existen
- cuál es el identificador canónico de cada brand
- qué valores base pertenecen a cada una

Ese catálogo es estable y debe existir antes de materializar flavors, targets o variantes concretas.

---

## Regla 3: Los valores de brand son base, no variante completa

Los valores propios de una brand son los que permanecen estables aunque cambie el entorno:

- display name base
- bundle/app id base
- recursos y assets de marca
- branding de producto

Los valores que cambian por despliegue o integración externa no pertenecen a `brand`; pertenecen a `env`.

---

## Regla 4: `brand` y `env` no deben absorberse mutuamente

Una brand no debe usarse para codificar diferencias que en realidad son de entorno.

Un entorno no debe usarse para codificar identidad de producto.

La variante final siempre surge de combinar:

- una identidad de marca
- un entorno operativo

Si una regla deja de tener sentido al cambiar solo la marca, es una regla de `brand`.
Si deja de tener sentido al cambiar solo el entorno, es una regla de `env`.

---

## Regla 5: La matriz de variantes consume el catálogo de brands

La semántica de variantes no inventa brands; consume el catálogo definido para el proyecto.

La matriz `brand × env` se construye a partir de:

- el catálogo de brands
- el catálogo de entornos

La skill de `environments` compone ambas dimensiones, pero no redefine qué es una brand.

---

## Regla 6: Las diferencias funcionales por marca pertenecen a arquitectura y app

Si una brand cambia:

- navegación
- composición de pantallas
- features visibles
- wiring de implementación

esas decisiones se coordinan con:

- `kb-kmm-app-layer`
- `kb-kmm-clean-architecture`

Esta skill solo define la semántica de la dimensión `brand`, no cómo se implementa cada diferencia en runtime.

---

## Regla 7: La implementación Android e iOS consumen la dimensión `brand`

Android e iOS materializan la dimensión `brand` con mecanismos distintos:

- flavors Android
- targets, schemes o configuración iOS

Pero la semántica base de brand vive aquí, no en la implementación de plataforma.
