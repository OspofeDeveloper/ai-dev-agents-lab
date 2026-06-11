---
name: kb-kmm-core-layer
description: "Capa core en proyectos KMM: dominio compartido, infraestructura transversal, criterios para subir responsabilidades desde features y reglas para evitar que core se convierta en un cajón desastre."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# Capa core KMM — Base de Conocimiento

## Regla 1: `core` contiene lo compartido y estable

La capa `core` existe para alojar piezas reutilizables y estables que no pertenecen a una única feature ni a la composición de `app`.

Su valor está en centralizar contratos y capacidades verdaderamente transversales sin acoplarlas a un dominio de feature concreto.

---

## Regla 2: `core` no sabe nada de features concretas ni de navegación de aplicación

`core` no puede depender de `features` ni de `app`, ni conocer sus decisiones de composición.

Por tanto, `core` no contiene:

- destinos de navegación global
- screens o ViewModels de feature
- reglas que mencionen features concretas
- composición dependiente de brand resuelta a nivel app

Si una pieza necesita conocer una feature concreta para existir, no pertenece a `core`.

---

## Regla 3: `core` puede contener dos tipos de verdad: dominio compartido e infraestructura compartida

Las responsabilidades válidas de `core` suelen caer en dos grandes grupos:

- dominio compartido: modelos, contratos y use cases usados por varias features
- infraestructura compartida: red, storage, logging, recursos, configuración técnica y otras capacidades transversales

Ambos tipos son válidos, pero no deben mezclarse sin criterio en una misma pieza.

---

## Regla 4: El dominio compartido de `core` debe ser realmente transversal

Un modelo o caso de uso pertenece a `core` solo si varias features lo necesitan con el mismo significado.

Señales válidas para subir algo a `core`:

- varias features consumen el mismo repositorio o contrato
- varias features comparten un mismo modelo de negocio
- varias features necesitan la misma regla o caso de uso

No se sube algo a `core` por anticipación ni por comodidad puntual.

---

## Regla 5: La infraestructura compartida de `core` debe estar desacoplada del dominio de feature

Las piezas técnicas compartidas de `core` existen para ofrecer capacidades reutilizables, no para codificar reglas de una feature concreta.

Ejemplos típicos:

- networking
- persistencia local
- logging
- recursos
- configuración transversal
- contratos de autenticación reutilizables

Si una pieza técnica está diseñada solo para una feature, debe vivir cerca de esa feature aunque use infraestructura de `core`.

---

## Regla 6: `core` no es un cajón desastre

No todo lo que “no sé dónde poner” pertenece a `core`.

No deben entrar en `core`:

- utilidades genéricas sin ownership claro
- abstracciones inventadas sin consumidores reales
- lógica extraída demasiado pronto
- piezas movidas solo para reducir imports o evitar pensar en el dominio correcto

Mover algo a `core` sin una razón arquitectónica clara solo desplaza el desorden a una capa más difícil de sanear.

---

## Regla 7: Un contrato sube a `core` cuando varias features dependen de él, no cuando una sola lo usa

Si un repositorio, modelo o caso de uso solo sirve a una feature, debe quedarse en esa feature.

Sube a `core` cuando:

- deja de pertenecer semánticamente a una sola feature
- varias features lo consumen de forma natural
- su significado ya es compartido en el sistema

`core` debe representar verdad común, no futuras posibilidades.

---

## Regla 8: `core` protege a las features de detalles de infraestructura compartida

Las features pueden depender de `core`, pero no deberían tener que reconstruir detalles repetidos de red, storage, auth, logging o configuración técnica transversal.

`core` actúa como punto de estabilización para esas capacidades, siempre que se expongan mediante contratos o límites claros.

---

## Regla 9: Los contratos de `core` deben sobrevivir a cambios de librería

Si una pieza de `core` define una abstracción compartida, esa abstracción no debe estar contaminada por detalles de una librería concreta salvo que esa skill sea explícitamente de implementación técnica.

Esto aplica especialmente a:

- contratos de networking
- contratos de auth
- persistencia abstraída
- logging o telemetría

La parte estable vive en `core`; la implementación concreta se especializa donde corresponda.

---

## Regla 10: `core` puede organizarse internamente por dominios transversales, no por features

La estructura interna de `core` debe reflejar capacidades compartidas, por ejemplo:

- `domain/`
- `network/`
- `storage/`
- `resources/`
- `auth/`
- `brand/`

La organización exacta puede variar, pero siempre debe expresar transversalidad y no dependencia de features concretas.

---

## Regla 11: `core` no sustituye a `app`

`core` no decide composición global ni routing de la aplicación.

No le corresponde:

- elegir qué screen se muestra
- resolver composición de pantallas agregadas
- tomar decisiones por brand a nivel de navegación
- actuar como composition root

Cuando `core` empieza a ensamblar la app, se rompe la frontera con `app`.

---

## Regla 12: `core` no sustituye a las features

`core` tampoco debe absorber reglas que siguen siendo propias de una sola feature.

Señales de error:

- modelos con nombre y significado ligados a una única feature
- use cases usados por una sola feature pero movidos “por limpieza”
- repositorios creados en `core` sin consumidores múltiples reales

Eso reduce la cohesión de la feature y hace que `core` pierda precisión semántica.

---

## Regla 13: Subir una pieza a `core` exige demostrar estabilidad y reutilización

Antes de mover algo desde una feature a `core`, comprobar:

- si la pieza tiene el mismo significado en más de una feature
- si será consumida realmente por varias features y no solo potencialmente
- si puede vivir en `core` sin mencionar dominios concretos de feature
- si moverla mejora la arquitectura en lugar de diluir ownership

Si la respuesta no es clara, la pieza debería seguir en la feature.

---

## Regla 14: `core` debe tener ownership semántico claro

Cada pieza en `core` debe responder con claridad a una de estas preguntas:

- qué contrato transversal define
- qué capacidad compartida ofrece
- qué modelo común representa
- qué infraestructura reutilizable encapsula

Si no se puede explicar con una frase simple por qué está en `core`, probablemente no debería estar ahí.

---

## Regla 15: Esta skill solo define reglas conceptuales de la capa `core`

Esta skill no define detalles concretos de Koin, Ktor, SQLDelight o cualquier otra tecnología.

- La skill de arquitectura global define la relación entre `app`, `features` y `core`
- La skill de features define qué debe quedarse dentro de una feature
- Las skills de networking, auth, DI o storage definen contratos e implementaciones específicas de cada dimensión técnica

Si una regla depende de una librería concreta, no pertenece aquí.
