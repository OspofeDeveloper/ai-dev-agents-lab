---
name: kb-kmm-clean-architecture
description: "Base de conocimiento de la arquitectura por capas en proyectos KMM: roles de app/core/features, dependencias permitidas, composición, navegación, agregación entre features y compartir datos sin acoplamiento."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Arquitectura por capas KMM — Base de Conocimiento

## Regla 1: La arquitectura define capas y fronteras, no tecnologías

Esta skill define la estructura arquitectónica estable del proyecto: capas, ownership, dependencias permitidas y reglas de composición.

Nunca impone librerías concretas como Ktor, Koin o un mecanismo específico de autenticación. Si una regla sigue siendo cierta aunque cambie la librería HTTP, DI o auth, pertenece aquí.

---

## Regla 2: Las capas reales del proyecto son `app`, `features` y `core`

La topología arquitectónica del proyecto es:

```text
app/ -> features/ -> core/
```

Este diagrama expresa solo la dirección conceptual de dependencias. No es una plantilla física de carpetas ni una estructura obligatoria 1:1 del repositorio.

La dirección de dependencias es siempre hacia dentro:

- `app` puede depender de `features` y `core`
- `features` puede depender de `core`
- `core` no depende de `features` ni de `app`

No se modela la arquitectura del proyecto como una separación abstracta `presentation/domain/data` repartida libremente por cualquier sitio. La unidad estructural autoritativa aquí es la capa `app` / `features` / `core`.

---

## Regla 3: Cada capa tiene una responsabilidad distinta

La arquitectura global separa tres dimensiones de verdad:

- `app`: composition root y decisiones de ensamblado global
- `features`: unidades autónomas de dominio y UI de producto
- `core`: dominio compartido e infraestructura transversal

Las reglas detalladas de cada capa viven en sus skills especializadas correspondientes. Esta skill solo fija la relación entre capas y sus fronteras globales.

---

## Regla 4: Las features son autónomas y no dependen entre sí

Cada feature es una unidad propia dentro de la capa `features`.

Las reglas globales son:

- una feature puede depender de `core`
- una feature no depende de otra feature
- una feature no decide composición global de aplicación

La microarquitectura interna de cada feature vive en la skill especializada de feature.

---

## Regla 5: `app` decide la composición global

La capa `app` resuelve navegación, ensamblado entre features y decisiones globales dependientes de contexto, brand o composición.

Las reglas detalladas de la capa `app` viven en su skill especializada. Esta skill solo fija que esas decisiones no pertenecen a `features` ni a `core`.

---

## Regla 6: `core` concentra lo compartido y transversal

La capa `core` agrupa contratos, dominio e infraestructura reutilizable entre múltiples features.

Las reglas detalladas de entrada, exclusión y organización interna de `core` viven en su skill especializada. Esta skill solo fija que `core` no conoce `features` concretas ni composición de `app`.

---

## Regla 7: La navegación se resuelve en `app`, no en las features

Las features pueden emitir hechos o callbacks, pero la navegación concreta pertenece a `app`.

Esto incluye:

- destinos globales
- routing dependiente de brand o contexto
- composición de pantallas agregadas

La política detallada de navegación y composición vive en la skill de `app`.

---

## Regla 8: Compartir datos entre features exige extraer la responsabilidad al nivel correcto

Si una feature necesita datos o lógica que también usa otra feature, no debe depender de esa otra feature.

Aplicar este árbol de decisión:

- si el dato viene de una fuente externa compartida, mover el repositorio a `core/domain`
- si varias features comparten una transformación o caso de uso, moverlo a `core/domain/usecase`
- si solo comparten estado efímero de UI dentro de una misma pantalla agregada, coordinarlo con un ViewModel de pantalla en `app`

Si esta situación se repite con frecuencia entre las mismas features, reevaluar si son realmente dos features separadas.

---

## Regla 9: Los detalles de infraestructura quedan encapsulados detrás de límites claros

HTTP, persistencia, auth y DI son detalles de infraestructura. Deben quedar encapsulados detrás de contratos o puntos de composición acordes con la capa que los consume.

La arquitectura fija:

- qué capa puede conocer cada detalle
- dónde vive cada implementación
- qué contratos o fronteras deben respetarse

La arquitectura no se redefine porque cambie una librería concreta.

---

## Regla 10: Esta skill define reglas conceptuales; los workflows y skills de capa solo las aplican

Las `wf-*` y las skills específicas de `app`, `core` y `feature` consultan esta skill para respetar la topología global del sistema.

Esta skill no define pasos operativos ni snippets de implementación concreta. Tampoco duplica reglas detalladas que ya viven en las skills especializadas de capa.
