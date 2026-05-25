# SDD Design — Diagramas de la fase de prototipado visual

Este documento contiene los diagramas detallados de la fase `design`: sistema visual, derivacion de vistas por feature y handoff a Stitch y a `plan`.

Para la vista global del sistema, usa [sdd/DIAGRAMS.md](/Users/oscar/Documents/GitHub/ai-dev-agents-lab/sdd/DIAGRAMS.md).

---

## 1. Posicion de Design en el pipeline

**Pregunta que responde:** ¿que resuelve `design` entre `spec` y `plan`?

```mermaid
flowchart LR
    SPEC["feature_spec.md"]
    DESIGN["design"]
    STITCH["Stitch"]
    PLAN["feature_plan.md"]

    SPEC -->|"wf-design-system"| DESIGN
    DESIGN -->|"DESIGN.md"| STITCH
    DESIGN -->|"flows/views/ui_prompt"| STITCH
    STITCH -->|"validacion visual con cliente"| PLAN

    style SPEC fill:#fff3e0,stroke:#f57c00
    style DESIGN fill:#f3e5f5,stroke:#8e24aa
    style STITCH fill:#e3f2fd,stroke:#1976d2
    style PLAN fill:#e8f5e9,stroke:#388e3c
```

**Mensaje clave:** `design` sirve para cerrar interfaz y flujos antes de cristalizar decisiones tecnicas en el plan.

---

## 2. Flujo interno de `wf-design-system`

**Pregunta que responde:** ¿como se genera o actualiza el `DESIGN.md` de producto?

```mermaid
flowchart TD
    Spec[feature_spec.md]
    Spec --> Check{"Spec valido y en sync?"}
    Check -->|No| Stop[Detener]
    Check -->|Si| Existing{"¿Ya existe DESIGN.md?"}
    Existing -->|Si| ReadCurrent[Leer DESIGN.md actual]
    Existing -->|No| NewSystem[Crear sistema visual base]
    ReadCurrent --> Agent["design-architect<br/>modo design-system"]
    NewSystem --> Agent
    Agent --> DesignFile[DESIGN.md]

    style DesignFile fill:#f3e5f5,stroke:#8e24aa
```

**Mensaje clave:** `DESIGN.md` es un artefacto de producto persistente, no algo efimero por feature.

---

## 3. Flujo interno de `wf-design-feature-prototype`

**Pregunta que responde:** ¿como se derivan los artefactos listos para Stitch desde un spec?

```mermaid
flowchart TD
    Spec[feature_spec.md]
    DesignFile[DESIGN.md]
    Spec --> Check{"Spec valido?"}
    Check -->|No| Stop[Detener]
    Check -->|Si| Agent["design-architect<br/>modo feature-prototype"]
    DesignFile --> Agent
    Agent --> Flows["<feature>_flows.md"]
    Agent --> Views["<feature>_views.md"]
    Agent --> Prompt["<feature>_ui_prompt.md"]

    style Flows fill:#ede7f6,stroke:#5e35b1
    style Views fill:#f3e5f5,stroke:#8e24aa
    style Prompt fill:#fce4ec,stroke:#d81b60
```

**Mensaje clave:** la fase produce tres artefactos distintos para evitar que todo el contrato visual quede enterrado dentro de un prompt.

---

## 4. Contrato de artefactos en Design

**Pregunta que responde:** ¿que aporta cada archivo de la fase?

```mermaid
flowchart LR
    subgraph Product["Nivel producto"]
        D["DESIGN.md<br/>tokens, componentes, tono"]
    end

    subgraph Feature["Nivel feature"]
        F["flows.md<br/>secuencias y transiciones"]
        V["views.md<br/>pantallas, componentes y estados"]
        P["ui_prompt.md<br/>ensamblaje para Stitch"]
    end

    D --> F
    D --> V
    F --> P
    V --> P
```

**Mensaje clave:** `DESIGN.md` define identidad reusable; `flows` captura el comportamiento navegacional; `views` es la SSoT de pantalla; `ui_prompt` solo ensambla todo eso para Stitch.

---

## 5. Handoff desde Design hacia Stitch y Plan

**Pregunta que responde:** ¿como se usa la salida de design despues de generarla?

```mermaid
flowchart TD
    Output["DESIGN.md + flows/views/ui_prompt"]
    Output --> Stitch[Stitch]
    Stitch --> Review{"¿Validado con cliente?"}
    Review -->|No| Iterate["Ajustar DESIGN.md o views/prompt"]
    Iterate --> Stitch
    Review -->|Si| Plan["wf-prepare-plan<br/>sobre feature_spec.md"]

    style Stitch fill:#e3f2fd,stroke:#1976d2
    style Plan fill:#e8f5e9,stroke:#388e3c
```

**Mensaje clave:** el plan no nace del mockup, sino del spec ya validado con el contrato visual despejado.
