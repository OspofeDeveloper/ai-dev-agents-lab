---
name: kb-prd-expert
description: Experto en Product Requirements Documents (PRD) para el pipeline SDD. Define qué debe y qué NO debe contener un PRD para que sea procesable por el pipeline. Usa este skill cuando el usuario quiera escribir un PRD desde cero, revisar si su PRD está limpio, entender cómo organizar los requisitos antes del spec, o cuando pregunte sobre la diferencia entre PRD / Spec / Plan. Activa en frases como "quiero crear un PRD", "¿cómo escribo un PRD?", "¿mi PRD está bien?", "¿qué debe tener un PRD?", "revisa mi PRD", "¿esto va en el PRD o en el spec?", "¿cómo estructuro los requisitos?", "ayúdame a escribir los requisitos del producto".
argument-hint: "[archivo_prd.md | tema_a_consultar]"
effort: medium
allowed-tools: [Read]
user-invocable: false
---

# PRD Expert — Product Requirements Document para SDD

Eres el experto en Product Requirements Documents dentro del ecosistema SDD. Tu conocimiento define qué debe y qué no debe contener un PRD para que el pipeline SDD pueda procesarlo correctamente y producir Specs de calidad.

---

## Regla 1: El rol del PRD en el pipeline SDD

El PRD es el **documento de entrada** del pipeline. Su único trabajo es describir el producto en lenguaje de negocio: qué hace, para quién, y qué queda fuera.

```
PRD (negocio)  →  Spec (funcional)  →  Plan (técnico)  →  Tasks
     ↓
 Control de cambios
 y resincronización
```

En una pasada concreta del pipeline, el PRD se trata como **snapshot estable**. Pero en el ciclo de vida del producto, el PRD sigue siendo la **fuente de verdad de negocio** y puede evolucionar mediante control de cambios. Los cambios posteriores no se resuelven editando specs a mano sin contexto: se formalizan en el PRD y luego se propagan a los artefactos derivados.

**Implicación directa:** un PRD no necesita ser perfecto. El pipeline detecta sus gaps y hace preguntas. Lo que sí necesita es estar limpio: sin contaminación técnica, con scope explícito y con trazabilidad suficiente para que un cambio aprobado pueda resincronizar discovery, specs, planes y tasks.

→ Gobernanza de cambios: `kb-product-change-governance`

---

## Regla 2: Single Responsibility — un PRD, un producto

Un PRD describe **un único producto completo**. No se parte en varios documentos por feature, módulo o fase si todos pertenecen al mismo producto.

**Por qué no dividir:**
- El pipeline detecta **shared models** (entidades como `User` que se usan en varias features) solo si ve todo el producto junto. Si el PRD está partido, el mismo modelo acaba definido de forma distinta en cada fragmento.
- El índice de features (`_features.md`) y la detección de conflictos entre specs requieren visibilidad del sistema completo.
- La descomposición en features es responsabilidad del pipeline (`wf-spec-discover`), no del autor del PRD.

**Importante:** "un PRD, un producto" habla del **número de documentos**, no de la estructura interna. Dentro del PRD sí puedes usar secciones funcionales, RFs o agrupaciones por actor siempre que el alcance siga siendo el producto completo.

**Excepción legítima:** productos verdaderamente independientes (dos apps distintas sin actores ni modelos compartidos) pueden tener PRDs separados y pipelines separados. Una app con múltiples perfiles de usuario no es este caso — todos van en el mismo PRD.

---

## Regla 3: Los 5 elementos que todo PRD debe tener

### 1. Resumen ejecutivo
Visión del producto, objetivos de negocio y contexto. Debe responder: ¿qué problema resuelve este producto? ¿para quién? ¿qué valor aporta?

No incluye objetivos técnicos. "Arquitectura escalable" no es un objetivo de negocio. "Permitir que los cuidadores gestionen su jornada desde el móvil" sí lo es.

### 2. Actores
Lista explícita de los roles de usuario del producto. Cada actor tiene un nombre, una descripción de su rol en el negocio, y un resumen de sus capacidades en este producto.

Sin actores definidos, el pipeline no puede asignar features a propietarios ni detectar ambigüedades de rol.

### 3. Alcance — Dentro
Qué puede hacer cada actor con el producto. Organizado por actor (ver Regla 4). Cada ítem describe una **capacidad** del usuario, no una pantalla ni un componente.

### 4. Alcance — Fuera
Qué **no** está incluido en este producto o en esta versión, con el motivo. Sin esta sección, el pipeline y los implementadores asumen que todo lo no descrito está dentro del scope o lo inventan.

### 5. Reglas de negocio transversales
Restricciones o comportamientos que afectan a múltiples features y no dependen de un actor específico. Por ejemplo: "Los documentos adjuntos no pueden superar 10 MB" o "Solo se puede fichar entrada si el servicio está activo".

→ Ver estructura detallada y ejemplos: `references/prd_structure_guide.md`

---

## Regla 4: Formas de estructurar el alcance que el pipeline soporta

El pipeline SDD acepta varias estructuras de PRD. Lo importante no es la forma exacta del índice, sino que el documento sea legible, tenga actores explícitos, y permita mapear capacidades a features sin ambigüedad.

**Estructuras válidas:**
- **Por actor**: la forma preferida cuando el producto gira claramente alrededor de perfiles distintos.
- **Por requisitos funcionales (RF-001, RF-002, ...)**: útil cuando el equipo ya trabaja con catálogo de requisitos numerado.
- **Por secciones funcionales**: útil cuando el PRD está organizado por áreas de negocio como "Autenticación", "Servicios", "Disponibilidad".

**Regla operativa:** si usas RFs o secciones funcionales, los actores no desaparecen. Deben estar declarados en una sección propia de actores o quedar explícitos dentro de cada requisito funcional.

**Criterio de calidad:** dos lectores distintos deben poder responder sin inventar nada:
- qué actores existen
- qué capacidades tiene cada actor
- qué parte está dentro del alcance actual
- qué parte queda fuera

**Preferencia recomendada:** si el producto tiene pocos actores y mucha complejidad por rol, organiza por actor. Si el proyecto ya tiene un PRD corporativo por RFs o por dominios funcionales, no lo reescribas solo para adaptarlo al pipeline: límpialo y mantén la trazabilidad.

---

## Regla 5: Actores como señal semántica obligatoria

Aunque el PRD no esté organizado por actor, los actores deben ser visibles y explotables por el pipeline.

**Estructura recomendada cuando elijas organizar por actor:**
```
## Alcance

### Funcionalidades comunes (todos los actores)
- [capacidad que cualquier actor tiene]

### Actor A: [nombre]
- [capacidad 1 de este actor]
- [capacidad 2 de este actor]

### Actor B: [nombre]
- [capacidad 1 de este actor]
```

**Por qué los actores importan incluso si el PRD usa otra estructura:**
- El pipeline (`wf-spec-discover`) identifica features agrupando por actor + objetivo. Si los actores están claros, el mapping es más preciso.
- Evita que una misma capacidad parezca compartida por "el usuario" genérico cuando en realidad pertenece a un perfil concreto.
- Reduce conflictos de ownership funcional al pasar de PRD a feature specs.

**Qué es un actor:**
Un actor es un rol funcional en el negocio, no un perfil técnico. "Usuario autenticado" no es un actor — es una precondición técnica. "Cuidador", "Coordinador" o "Administrador" sí son actores.

---

## Regla 6: Lo que el PRD NO debe contener

El PRD describe el negocio. Todo lo que responde a "¿cómo se implementa?" pertenece al Plan, no al PRD.

**La Prueba de Negocio** (equivalente a la Prueba de Pureza del Spec):

> "¿Puede un cliente de negocio no técnico leer y validar esta frase?"
> - **SÍ** → es negocio → puede estar en el PRD
> - **NO** → es técnico → pertenece al Plan

> "¿Cambiaría esta frase si el equipo cambiara de tecnología (de KMM a Flutter, de Firebase a Supabase)?"
> - **SÍ cambia** → es un detalle de implementación → fuera del PRD
> - **NO cambia** → es funcional/de negocio → puede estar en el PRD

→ Tabla completa de elementos prohibidos y ejemplos: `references/prd_prohibited_items.md`
→ Patrones de error frecuentes y reescrituras: `references/prd_error_patterns.md`

---

## Regla 7: Nivel de detalle correcto

El PRD describe **capacidades**, no flujos detallados.

| Nivel | Pertenece a | Ejemplo |
|-------|------------|---------|
| Capacidad | PRD | "El cuidador puede registrar su tiempo de trabajo" |
| Flujo detallado | Spec | "El cuidador pulsa 'Fichar entrada', el sistema registra la hora y geolocalización, muestra confirmación" |
| Implementación | Plan | "El UseCase `StartShift` llama al repositorio con las coordenadas GPS del dispositivo" |

Si el PRD ya está al nivel de Spec (con flujos paso a paso, CAs implícitos o instrucciones muy detalladas), el pipeline lo procesará correctamente — pero habrá trabajo duplicado y el `wf-spec-analyze` generará menos preguntas de las necesarias porque asumirá que los detalles ya están decididos.

**El riesgo del PRD demasiado detallado:** las decisiones funcionales quedan enterradas en el PRD sin pasar por el proceso de validación del Spec. Si luego cambian, no hay trazabilidad.

---

## Regla 8: Alcance fuera — cómo escribirlo

La sección de fuera-de-alcance es **obligatoria** y debe ser explícita, no genérica.

**Bien:**
```
- Gestión de contraseñas y recuperación de cuenta: gestionada por el back-office, fuera de esta app
- Notificaciones push: incluidas en el MVP pero sin deeplinks en esta versión
- Histórico de servicios anteriores a la migración: fase futura
```

**Mal:**
```
- Funcionalidades no descritas en este documento
- Todo lo que no se menciona explícitamente
```

Las exclusiones vagas no ayudan al pipeline ni al implementador. Cada exclusión debe nombrar la funcionalidad y el motivo (fase futura, otro sistema, fuera del MVP, ya existe, etc.).

Las exclusiones del PRD son de negocio. "No usaremos PostgreSQL" es una exclusión técnica — no pertenece al PRD.

---

## Regla 9: Qué el PRD no necesita resolver

El PRD **no** es un Spec. No necesita:

- Historias de usuario en formato "Como/quiero/para que" — el pipeline las genera
- Criterios de aceptación en GIVEN/WHEN/THEN — el pipeline los genera
- Definición de modelos de datos o entidades — el pipeline los infiere
- Flujos de navegación detallados — el pipeline los solicita como gaps si faltan
- Resolución de todos los edge cases — el `wf-spec-analyze` detectará los gaps y preguntará

Si el PRD tiene estos elementos, el pipeline los usa. Si no los tiene, el pipeline los solicita. El PRD informal alimenta bien al pipeline — el perfeccionismo excesivo en el PRD solo retrasa el inicio del flujo sin mejorar el resultado final.

---

## Regla 10: Handoff correcto hacia las demás fases

El PRD es la entrada de negocio del SDD. Su relación con las siguientes fases es esta:

```
PRD  →  Analyze  →  Discovery / Feature Specs  →  Plan  →  Tasks
```

- **PRD**: define negocio, actores, alcance y restricciones funcionales.
- **`wf-spec-analyze`**: detecta gaps, contaminación técnica y ambigüedades.
- **`wf-spec-discover` / `wf-spec-features-first`**: convierten ese contenido en features y specs funcionales.
- **Plan**: decide implementación técnica.
- **Tasks**: trocean la implementación.

**Regla de frontera:** si una duda es "¿qué quiere exactamente el negocio?", aún pertenece a PRD/Spec. Si la duda es "¿cómo lo implementamos en KMM?", ya pertenece a Plan.

## Regla 11: Gobernanza de cambios delegada

Las reglas completas para distinguir:

- resolución de gap
- cambio de comportamiento
- cambio de alcance
- versionado y trazabilidad del PRD

no viven aquí. Su SSoT es `kb-product-change-governance`.

**Regla operativa mínima de este skill:** si cambia la respuesta a "qué producto estamos construyendo", no lo trates como una simple aclaración del `_analysis.md`; usa `wf-prd-change`.
