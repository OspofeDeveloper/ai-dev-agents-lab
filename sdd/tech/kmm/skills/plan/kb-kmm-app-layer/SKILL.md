---
name: kb-kmm-app-layer
description: "Base de conocimiento de la capa app en proyectos KMM: composition root, navegación, composición entre features, coordinación de estado efímero de pantalla y decisiones dependientes de brand o contexto."
argument-hint: ""
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Capa app KMM — Base de Conocimiento

## Regla 1: `app` es el composition root de la aplicación

La capa `app` existe para ensamblar piezas ya definidas en `features` y `core`. Su responsabilidad es decidir cómo se conectan, no redefinir su lógica interna.

`app` puede conocer múltiples features y piezas compartidas porque su trabajo es componer la aplicación final.

---

## Regla 2: `app` no contiene dominio de feature ni pantallas propias de negocio

`app` no debe absorber responsabilidades que pertenecen a una feature.

No debe contener:

- lógica de negocio de una feature
- repositorios o use cases que solo tengan sentido para una feature concreta
- screens que representen un dominio de feature
- modelos de dominio específicos de una feature

Si una pieza tiene semántica funcional propia y no solo de composición, probablemente no pertenece a `app`.

---

## Regla 3: La navegación global vive en `app`

Las decisiones de navegación global pertenecen a `app`, porque dependen de la composición total de la aplicación.

`app` define:

- el grafo de navegación
- los destinos globales
- cómo se conectan callbacks de features con rutas concretas
- cómo cambia el routing según brand o contexto

Las features no conocen rutas ni controladores de navegación global.

---

## Regla 4: `app` traduce hechos de feature a navegación concreta

Las features emiten hechos, eventos o efectos. `app` decide qué hacer con ellos en términos de navegación y composición.

La regla estable es:

- la feature expresa qué ocurrió
- `app` decide adónde ir o qué composición activar

Esto mantiene a las features reutilizables y evita acoplarlas a una única navegación.

---

## Regla 5: La composición entre features se resuelve en `app`

Cuando una pantalla combina contenido de varias features, la decisión de ensamblado pertenece a `app`.

`app` puede:

- decidir qué features aparecen en una pantalla compuesta
- pasar slots o callbacks a una screen agregadora
- omitir o incluir secciones según el contexto

Las features no deben importarse mutuamente para resolverse entre sí.

---

## Regla 6: Las decisiones dependientes de brand, flavor o contexto global viven en `app`

Si una decisión cambia según brand, flavor, entorno o una condición global de aplicación, su lugar natural es `app`.

Ejemplos típicos:

- routing distinto por brand
- composición distinta de una pantalla por brand
- selección de una implementación concreta en el composition root

Las features no deben conocer estas variantes salvo a través de contratos transversales ya resueltos.

---

## Regla 7: Un ViewModel en `app` solo coordina estado efímero de pantalla compuesta

`app` puede tener ViewModels propios cuando necesita coordinar estado efímero entre varias secciones renderizadas dentro de una misma pantalla compuesta.

Ese ViewModel es válido solo si su responsabilidad es:

- coordinar estado temporal de UI entre varias features
- mediar callbacks de composición
- sostener estado que no pertenece a una sola feature

No es válido usar `app` ViewModels para mover lógica de negocio fuera de las features o esconder una feature mal modelada.

---

## Regla 8: `app` puede cablear implementaciones, pero no definir contratos de dominio compartido

`app` decide qué implementación concreta usar al componer la app, pero no es el sitio donde viven contratos estables del dominio o de la infraestructura compartida.

Por tanto:

- el contrato vive en `core` o en la feature correspondiente
- la implementación concreta puede ser elegida o ensamblada desde `app` si la decisión es de composición

`app` selecciona y conecta; no define la verdad estructural compartida.

---

## Regla 9: `app` no sustituye a `core`

Si una pieza empieza a ser reutilizable, estable y compartida por múltiples features o por varias pantallas, debe evaluarse si realmente pertenece a `core`.

`app` no es un lugar para acumular:

- contratos compartidos
- modelos de dominio transversales
- lógica reutilizable entre múltiples contextos
- infraestructura de propósito general

Esas piezas convierten a `app` en una pseudo-capa de dominio compartido, y eso rompe su responsabilidad.

---

## Regla 10: `app` no sustituye a una feature

Cuando una pieza crece en complejidad funcional y deja de ser mera composición, debe migrar a una feature real.

Señales de deriva:

- una screen en `app` empieza a tener lógica de negocio propia
- un ViewModel de `app` empieza a orquestar casos de uso de un dominio concreto
- aparecen estados, eventos y efectos que ya describen un dominio funcional completo

En ese punto, `app` está absorbiendo una feature encubierta.

---

## Regla 11: La capa `app` optimiza claridad de ensamblado

El objetivo de `app` es que la composición global sea visible y fácil de razonar.

Al leer `app` debería quedar claro:

- qué destinos existen
- qué feature responde a cada destino
- cómo se componen las pantallas agregadas
- dónde se toman decisiones globales de brand o contexto

Si para entender la composición global hay que inspeccionar varias features acopladas entre sí, la arquitectura está perdiendo claridad.

---

## Regla 12: Esta skill solo define reglas conceptuales de la capa `app`

Esta skill no define APIs de navegación concretas, librerías de DI ni detalles de implementación.

- La skill de arquitectura global define la relación entre `app`, `features` y `core`
- La skill de features define la microarquitectura interna de cada feature
- La skill de DI define cómo registrar dependencias
- La skill de navegación concreta define detalles operativos si el stack los requiere

Si una regla depende de Koin, Voyager, Navigation Compose o cualquier librería concreta, no pertenece aquí.
