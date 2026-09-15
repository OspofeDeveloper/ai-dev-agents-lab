# SDD Spec — Diagramas de Specify y Decompose

Este documento contiene los diagramas detallados de la fase `spec`: análisis, discovery, generación por feature, evolución y validación.

Para la vista global del sistema, usa [sdd/DIAGRAMS.md](../DIAGRAMS.md).

---

## 1. Flujo features-first completo

**Pregunta que responde:** ¿qué pasos internos sigue la generación de specs por feature?

```mermaid
flowchart TD
    PRD[PRD.md]
    PRD --> Analyze["wf-spec-analyze"]
    Analyze --> Analysis[prd_analysis.md]
    Analysis --> Gaps{"¿Gaps criticos<br/>pendientes?"}
    Gaps -->|Si| Stop1["Responder analysis<br/>o usar override explicito"]
    Gaps -->|No| Discover["wf-spec-discover"]
    Discover --> Discovery[prd_discovery.md]
    Discovery --> Size{"¿Mas de 5 features?"}
    Size -->|Si| Subset["Elegir subset<br/>--features"]
    Size -->|No| Generate["Generacion"]
    Subset --> FF["wf-spec-features-first"]
    Generate --> FF
    FF --> Features[features/<x>/spec/<x>_spec.md]
    Features --> Conflict["wf-spec-conflict"]
    Conflict --> Readiness["wf-spec-readiness"]

    style Analysis fill:#fff8e1,stroke:#f9a825
    style Discovery fill:#fff3e0,stroke:#f57c00
    style Features fill:#e8f5e9,stroke:#388e3c
```

**Mensaje clave:** `wf-spec-features-first` no es un generador ciego; está protegido por analysis, guardrails de scope y control de coste.

---

## 2. Arquitectura interna de la fase Spec

**Pregunta que responde:** ¿cómo se reparten responsabilidades entre workflows, agentes y knowledge bases?

```mermaid
flowchart TB
    subgraph L1["Workflows"]
        W1["wf-spec-analyze"]
        W2["wf-spec-discover"]
        W3["wf-spec-fast-track"]
        W4["wf-spec-features-first"]
        W5["wf-spec-delta apply / gap-resolve / sync-from-prd / amend"]
        W6["wf-spec-validate / conflict / readiness / sync-impact"]
        W7["wf-spec-from-code (brownfield)"]
    end

    subgraph L2["Agentes worker"]
        A1["sdd-spec-explorer"]
        A3["sdd-spec-writer"]
        A4["sdd-spec-auditor"]
    end

    subgraph L3["Knowledge bases"]
        K1["kb-spec-expert"]
        K2["kb-decompose-expert"]
        K3["kb-conflict-expert"]
        K4["kb-gap-conventions"]
        K5["kb-traceability-rules"]
        K6["kb-prd-expert<br/>kb-product-change-governance"]
        K7["kb-spec-characterization"]
    end

    W1 --> A1
    W2 --> A1
    W3 --> A3
    W4 --> A3
    W5 --> A3
    W6 --> A4
    W7 --> A3
    L3 -.-> L2
```

**Mensaje clave:** en `spec`, la separacion entre explorar, escribir y auditar es parte del diseño, no accidental.

---

## 3. Fast-track paralelo por feature

**Pregunta que responde:** ¿qué hace exactamente el tramo paralelo del workflow features-first?

```mermaid
flowchart LR
    Discovery[prd_discovery.md]
    Discovery --> F1["F-001"]
    Discovery --> F2["F-002"]
    Discovery --> F3["F-003"]

    F1 --> A1["sdd-spec-writer<br/>wf-spec-fast-track"]
    F2 --> A2["sdd-spec-writer<br/>wf-spec-fast-track"]
    F3 --> A3["sdd-spec-writer<br/>wf-spec-fast-track"]

    A1 --> S1["features/f1/spec/f1_spec.md"]
    A2 --> S2["features/f2/spec/f2_spec.md"]
    A3 --> S3["features/f3/spec/f3_spec.md"]

    S1 --> Hub[["sdd-features-index.py<br/>regenera prd_features.md"]]
    S2 --> Hub
    S3 --> Hub
```

**Mensaje clave:** el paralelismo vive en la generacion por feature; `_features.md` no se escribe a mano ni se consolida con prosa — es un **indice generado** por `sdd-features-index.py` a partir del discovery + los specs en disco + el readiness report. Un conflicto de merge sobre el hub es ruido: se regenera tras el merge.

---

## 4. Mantenimiento de specs existentes

**Pregunta que responde:** ¿qué rutas existen cuando el spec ya esta creado?

```mermaid
flowchart TD
    Existing[feature_spec.md existente]
    Existing --> ChangeType{"¿Que ha pasado?"}

    ChangeType -->|Nueva necesidad incremental| Delta["wf-spec-delta"]
    ChangeType -->|HU incompleta por gap pendiente| Gap["wf-spec-gap-resolve"]
    ChangeType -->|CA ambiguo descubierto al implementar| Amend["wf-spec-amend"]
    ChangeType -->|Edicion manual a revisar| Validate["wf-spec-validate"]
    ChangeType -->|Posible solapamiento entre features| Conflict["wf-spec-conflict"]
    ChangeType -->|Cambio real en el PRD| Impact["wf-prd-sync-impact<br/>(mide: que quedo stale)"]
    ChangeType -->|El producto retira la capacidad| Retire["wf-spec-retire"]

    Impact --> Decide{"¿Que features<br/>resincronizar?"}
    Decide -->|las afectadas| Sync["wf-spec-sync-from-prd<br/>(aplica)"]
    Decide -->|el PRD ya no la contempla| Retire

    Delta --> Updated[spec actualizado]
    Gap --> Updated
    Amend --> Updated
    Validate --> Updated
    Conflict --> Updated
    Sync --> Updated
    Retire --> Retired["spec RETIRADO — fin de la feature"]

    Retired -.->|"la decision se revierte<br/>(wf-spec-retire reactivate)"| Existing
```

**Mensaje clave:** no todo cambio se resuelve regenerando desde cero; `spec` tiene caminos quirurgicos para evolucion, sync y cierre. **Seis llevan al spec actualizado y una no**: la baja es la unica salida terminal, y el ID de la feature se conserva sin reutilizarse.

**Tres aristas que el diagrama tiene implicitas y conviene no saltarse:**

- **Medir antes de aplicar.** Un cambio de PRD no entra directo en `wf-spec-sync-from-prd`: primero `wf-prd-sync-impact` dice **que** quedo `stale` o `needs_review`, y revisar ese informe es un checkpoint humano bloqueante. Es tambien donde se separan las dos salidas: una feature afectada se resincroniza, una que el PRD ya no contempla se da de baja — y esa segunda no se decide en un fork.
- **La baja cierra tambien la puerta que este diagrama no dibuja ([[D-080]]).** Aqui solo entran las
  vias que arrancan **desde un spec existente**. Las que lo **regeneran** arrancan desde el PRD o
  desde el codigo —fast-track, caracterizacion, generacion por feature— y aterrizan en el mismo
  fichero: tambien paran ante un `RETIRADO`, lo dicen y no lo pisan. Y un spec retirado queda fuera
  del analisis de conflictos: un choque contra algo que no se va a implementar no es un conflicto.
- **La reactivacion es la unica vuelta atras, y no restaura sellos.** Devuelve el spec a `BORRADOR`, no a `VALIDADO`; el plan sigue en `BORRADOR` desde la baja. Ningun otro camino sale de `RETIRADO`: desde [[D-078]], tampoco el `--unseal` con el que cierran delta, amend y gap-resolve.
