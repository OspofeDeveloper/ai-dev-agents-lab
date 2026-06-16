# SDD Plan — Diagramas de la fase de cierre técnico

Este documento contiene los diagramas detallados de la fase `plan`: generación del `_plan.md`, resolución del handoff de Design, auditoría formal y promoción a `VALIDADO`.

Para la vista global del sistema, usa [sdd/DIAGRAMS.md](../DIAGRAMS.md).

---

## 1. Posición de Plan en el pipeline

**Pregunta que responde:** ¿qué resuelve `plan` entre `design` y `tasks`?

```mermaid
flowchart LR
    SPEC["feature_spec.md<br/>validado"]
    DESIGN["DESIGN.md + flows + views<br/>(cuando aplica)"]
    PREP["wf-prepare-plan"]
    DRAFT["feature_plan.md<br/>Estado: BORRADOR"]
    VALIDATE["wf-plan-validate"]
    OK["feature_plan.md<br/>Estado: VALIDADO"]
    TASKS["wf-prepare-tasks"]

    SPEC --> PREP
    DESIGN --> PREP
    PREP --> DRAFT
    DRAFT --> VALIDATE
    VALIDATE --> OK
    OK --> TASKS

    style SPEC fill:#fff3e0,stroke:#f57c00
    style DESIGN fill:#f3e5f5,stroke:#8e24aa
    style DRAFT fill:#fff8e1,stroke:#f9a825
    style OK fill:#e8f5e9,stroke:#388e3c
    style TASKS fill:#e0f2f1,stroke:#00897b
```

**Mensaje clave:** `plan` no trocea trabajo; cierra decisiones arquitectónicas y deja un `_plan.md` primero en `BORRADOR` y solo luego en `VALIDADO`.

---

## 2. Flujo interno de `wf-prepare-plan`

**Pregunta que responde:** ¿qué validaciones y bifurcaciones existen antes de escribir el `_plan.md`?

```mermaid
flowchart TD
    Start["generate <feature_spec.md>"]
    Start --> Parse["Parsear argumentos"]
    Parse --> SpecCheck{"¿Existe el spec<br/>y parece un Spec SDD?"}
    SpecCheck -->|No| StopSpec["Detener"]
    SpecCheck -->|Si| ReadyCheck{"¿Hay [INCOMPLETO],<br/>[CRITICO] o status_sync no fiable?"}
    ReadyCheck -->|Si| StopReady["Bloquear por Spec no listo"]
    ReadyCheck -->|No| Shared["Leer _features.md<br/>si existe"]
    Shared --> DesignRule{"¿La regla canonica<br/>exige Design?"}
    DesignRule -->|No| PromptNoUI["Prompt: feature sin<br/>surface UI visible"]
    DesignRule -->|Si| DesignFiles{"¿Existen DESIGN.md,<br/>flows y views?"}
    DesignFiles -->|No| StopDesign["Bloquear por handoff<br/>de Design incompleto"]
    DesignFiles -->|Si| A11y{"¿DESIGN.md incluye<br/>## Accessibility?"}
    A11y -->|No| StopA11y["Bloquear por gap<br/>de accesibilidad"]
    A11y -->|Si| PromptUI["Adjuntar DESIGN.md,<br/>flows y views"]
    PromptNoUI --> Agent["Delegar a plan-architect<br/>modo generate-plan"]
    PromptUI --> Agent
    Agent --> Gaps{"¿Devuelve gaps?"}
    Gaps -->|DESIGN_GAP| StopDG["No escribir plan"]
    Gaps -->|TECH_GAP| StopTG["No escribir plan"]
    Gaps -->|TRACE_GAP o PLAN_GAP| StopPG["No escribir plan"]
    Gaps -->|No| Write["Escribir <feature>_plan.md"]
    Write --> Draft["Estado: BORRADOR"]

    style Draft fill:#fff8e1,stroke:#f9a825
    style StopReady fill:#ffebee,stroke:#c62828
    style StopDesign fill:#ffebee,stroke:#c62828
    style StopA11y fill:#ffebee,stroke:#c62828
    style StopDG fill:#ffebee,stroke:#c62828
    style StopTG fill:#ffebee,stroke:#c62828
    style StopPG fill:#ffebee,stroke:#c62828
```

**Mensaje clave:** `wf-prepare-plan` no genera nada si el Spec no está listo o si falta handoff normativo de Design cuando la feature lo necesita.

---

## 3. Regla de decisión: cuándo Design es obligatorio

**Pregunta que responde:** ¿en qué casos `plan` debe bloquearse esperando handoff visual?

```mermaid
flowchart TD
    Change["Cambio o feature a planificar"]
    Change --> Rule{"¿El Plan debe cerrar UI visible,<br/>navegacion o a11y visual?"}

    Rule -->|Si| Need["Design obligatorio"]
    Rule -->|No| Skip["Design no obligatorio"]

    Need --> NeedFiles["Requerir DESIGN.md<br/>+ <feature>_flows.md<br/>+ <feature>_views.md"]
    NeedFiles --> NeedA11y["Exigir ## Accessibility<br/>en DESIGN.md"]
    NeedA11y --> ContinueUI["Continuar con handoff<br/>normativo adjunto"]

    Skip --> ContinueNoUI["Continuar como cambio tecnico<br/>sin surface UI visible"]

    style Need fill:#ffebee,stroke:#c62828
    style Skip fill:#e8f5e9,stroke:#388e3c
    style ContinueUI fill:#f3e5f5,stroke:#8e24aa
    style ContinueNoUI fill:#e3f2fd,stroke:#1976d2
```

**Mensaje clave:** la obligación de Design depende del tipo de verdad que el Plan debe cerrar, no de una preferencia del agente ni de si “sería útil” tener mocks.

---

## 4. Arquitectura interna de la fase Plan

**Pregunta que responde:** ¿cómo se reparten responsabilidades entre workflows, agente y knowledge base?

```mermaid
flowchart TB
    subgraph L1["Workflows"]
        W1["wf-prepare-plan"]
        W2["wf-plan-validate"]
    end

    subgraph L2["Agente worker"]
        A1["plan-architect"]
    end

    subgraph L3["Knowledge bases"]
        K1["kb-plan-expert"]
        K2["kb-spec-expert"]
        K3["kb-a11y-expert"]
    end

    W1 --> A1
    W2 --> A1
    L3 -.-> A1
```

**Mensaje clave:** los workflows no diseñan ni auditan por sí mismos; reúnen contexto, aplican gates y delegan el trabajo técnico real a `plan-architect`.

---

## 5. Flujo interno de `wf-plan-validate`

**Pregunta que responde:** ¿cómo se sella un `_plan.md` como `VALIDADO` o se devuelve a `BORRADOR`?

```mermaid
flowchart TD
    Start["<feature>_plan.md"]
    Start --> PlanCheck{"¿Existe y parece<br/>un Plan SDD?"}
    PlanCheck -->|No| StopPlan["Detener"]
    PlanCheck -->|Si| FooterCheck{"¿Ya declara gaps<br/>abiertos en el footer?"}
    FooterCheck -->|Si| Demote["Forzar Estado: BORRADOR"]
    FooterCheck -->|No| Context["Resolver Spec origen,<br/>Design y shared models"]
    Demote --> StopOpen["No validar hasta<br/>resolver gaps"]
    Context --> Agent["Delegar a plan-architect<br/>modo validate-plan"]
    Agent --> Result{"¿Respuesta OK?"}
    Result -->|Si| Promote["Actualizar Estado: VALIDADO"]
    Promote --> Clean["Persistir cuatro lineas<br/>de gaps = ninguno"]
    Result -->|No| Findings["Persistir bloque normalizado<br/>de gaps"]
    Findings --> Back["Actualizar Estado: BORRADOR"]

    style Promote fill:#e8f5e9,stroke:#388e3c
    style Clean fill:#e8f5e9,stroke:#388e3c
    style Demote fill:#fff8e1,stroke:#f9a825
    style Back fill:#ffebee,stroke:#c62828
    style StopOpen fill:#ffebee,stroke:#c62828
```

**Mensaje clave:** la validación no reescribe arquitectura; solo certifica si el plan puede pasar a `tasks` y persiste su estado operativo.

---

## 6. Taxonomía de gaps y efecto operativo

**Pregunta que responde:** ¿qué tipos de gaps existen y qué bloquean exactamente?

```mermaid
flowchart LR
    DG["DESIGN_GAP"]
    TG["TECH_GAP"]
    TR["TRACE_GAP"]
    PG["PLAN_GAP"]

    DG --> B1["Bloquea generacion<br/>o validacion"]
    TG --> B2["Bloquea cierre tecnico<br/>del plan"]
    TR --> B3["Bloquea promotion<br/>a VALIDADO"]
    PG --> B4["Bloquea promotion<br/>a VALIDADO"]

    B1 --> Draft["Estado resultante:<br/>BORRADOR o sin archivo"]
    B2 --> Draft
    B3 --> Draft
    B4 --> Draft

    style Draft fill:#fff8e1,stroke:#f9a825
```

**Mensaje clave:** la fase `plan` usa solo cuatro tipos normativos de gap; cualquier hallazgo debe caer en una de esas categorías para mantener el gate estable.
