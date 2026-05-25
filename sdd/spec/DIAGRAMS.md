# SDD Spec — Diagramas de Specify y Decompose

Este documento contiene los diagramas detallados de la fase `spec`: análisis, discovery, generación por feature, evolución y validación.

Para la vista global del sistema, usa [sdd/DIAGRAMS.md](/Users/oscar/Documents/GitHub/ai-dev-agents-lab/sdd/DIAGRAMS.md).

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
    FF --> Features[features/<x>/<x>_spec.md]
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
        W5["wf-spec-delta / gap-resolve / validate / conflict / readiness"]
    end

    subgraph L2["Agentes worker"]
        A1["sdd-spec-explorer"]
        A2["sdd-spec-planner"]
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
    end

    W1 --> A1
    W2 --> A1
    W3 --> A3
    W4 --> A3
    W5 --> A4
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

    A1 --> S1["features/f1/f1_spec.md"]
    A2 --> S2["features/f2/f2_spec.md"]
    A3 --> S3["features/f3/f3_spec.md"]

    S1 --> Hub[prd_features.md consolidado]
    S2 --> Hub
    S3 --> Hub
```

**Mensaje clave:** el paralelismo vive en la generacion por feature; la consolidacion de `_features.md` vuelve a ser centralizada.

---

## 4. Mantenimiento de specs existentes

**Pregunta que responde:** ¿qué rutas existen cuando el spec ya esta creado?

```mermaid
flowchart TD
    Existing[feature_spec.md existente]
    Existing --> ChangeType{"¿Que ha pasado?"}

    ChangeType -->|Nueva necesidad incremental| Delta["wf-spec-delta"]
    ChangeType -->|HU incompleta por gap pendiente| Gap["wf-spec-gap-resolve"]
    ChangeType -->|Edicion manual a revisar| Validate["wf-spec-validate"]
    ChangeType -->|Posible solapamiento entre features| Conflict["wf-spec-conflict"]
    ChangeType -->|Cambio real en el PRD| Sync["wf-spec-sync-from-prd"]

    Delta --> Updated[spec actualizado]
    Gap --> Updated
    Validate --> Updated
    Conflict --> Updated
    Sync --> Updated
```

**Mensaje clave:** no todo cambio se resuelve regenerando desde cero; `spec` tiene caminos quirurgicos para evolucion y sync.
