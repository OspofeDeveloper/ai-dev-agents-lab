# SDD Design — Diagramas de la fase de prototipado visual

Este documento contiene los diagramas detallados de la fase `design`: intake de direccion visual, sistema visual, derivacion de vistas por feature y handoff a Stitch y a `plan`.

Para la vista global del sistema, usa [sdd/DIAGRAMS.md](../DIAGRAMS.md).

---

## 1. Posicion de Design en el pipeline

**Pregunta que responde:** ¿que resuelve `design` entre `spec` y `plan`?

```mermaid
flowchart LR
    SPEC["feature_spec.md"]
    MOOD["wf-design-moodboard<br/>(opcional)"]
    MOODFILE["_design_moodboard.md"]
    INTAKE["wf-design-intake"]
    BRIEF["DESIGN_BRIEF.md<br/>(gate obligatorio)"]
    DISCOVER["wf-design-discover<br/>(opcional)"]
    DISCOVERY["_design_discovery.md"]
    SYSTEM["wf-design-system"]
    DESIGN["DESIGN.md<br/>(semver)"]
    VALIDATE["wf-design-validate"]
    A11Y["wf-design-a11y-audit"]
    DELTA["wf-design-delta"]
    BRANCH["wf-design-branch"]
    VARIANT["wf-design-variant"]
    FEATURE["wf-design-feature-prototype"]
    BUNDLE["flows / views / ui_prompt"]
    EXPORT["wf-design-export"]
    TOKENS["tokens/<br/>(CSS, Compose, SwiftUI, ...)"]
    FEEDBACK["wf-design-feedback"]
    STITCH["Stitch"]
    PLAN["feature_plan.md"]

    SPEC --> MOOD
    MOOD --> MOODFILE
    SPEC --> INTAKE
    MOODFILE -.alimenta.-> INTAKE
    INTAKE --> BRIEF
    BRIEF --> DISCOVER
    DISCOVER --> DISCOVERY
    BRIEF --> SYSTEM
    DISCOVERY --> SYSTEM
    SPEC --> SYSTEM
    SYSTEM --> DESIGN
    DESIGN --> VALIDATE
    DESIGN --> A11Y
    DESIGN -. iterar .-> DELTA
    DELTA --> DESIGN
    DESIGN -. explorar .-> BRANCH
    BRANCH -. merge .-> DESIGN
    DESIGN --> FEATURE
    BRIEF --> FEATURE
    FEATURE --> BUNDLE
    SPEC -. A/B .-> VARIANT
    DESIGN -. A/B .-> VARIANT
    DESIGN --> EXPORT
    EXPORT --> TOKENS
    BUNDLE --> STITCH
    DESIGN --> STITCH
    STITCH -->|"validacion con cliente"| FEEDBACK
    FEEDBACK -. triage .-> INTAKE
    FEEDBACK -. triage .-> DELTA
    FEEDBACK --> PLAN
    TOKENS --> PLAN

    style SPEC fill:#fff3e0,stroke:#f57c00
    style MOOD fill:#e0f7fa,stroke:#00838f
    style MOODFILE fill:#e0f7fa,stroke:#00838f
    style INTAKE fill:#fff8e1,stroke:#f9a825
    style BRIEF fill:#fff8e1,stroke:#f9a825
    style DISCOVER fill:#e0f7fa,stroke:#00838f
    style DISCOVERY fill:#e0f7fa,stroke:#00838f
    style SYSTEM fill:#f3e5f5,stroke:#8e24aa
    style DESIGN fill:#f3e5f5,stroke:#8e24aa
    style VALIDATE fill:#ede7f6,stroke:#5e35b1
    style A11Y fill:#ede7f6,stroke:#5e35b1
    style DELTA fill:#ede7f6,stroke:#5e35b1
    style BRANCH fill:#fff3e0,stroke:#fb8c00
    style VARIANT fill:#fff3e0,stroke:#fb8c00
    style FEATURE fill:#f3e5f5,stroke:#8e24aa
    style BUNDLE fill:#fce4ec,stroke:#d81b60
    style EXPORT fill:#e8f5e9,stroke:#43a047
    style TOKENS fill:#e8f5e9,stroke:#43a047
    style FEEDBACK fill:#fce4ec,stroke:#d81b60
    style STITCH fill:#e3f2fd,stroke:#1976d2
    style PLAN fill:#e8f5e9,stroke:#388e3c
```

**Mensaje clave:** la fase opera en siete capas con responsabilidad unica: inspiracion (`moodboard`), intake (`brief`), discovery (`referencias`), generacion (`system` + `feature-prototype`), evolucion (`validate` + `delta`), exploracion (`branch` + `variant`) y handoff (`export` + `a11y-audit` + `feedback`). El `DESIGN_BRIEF.md` es gate obligatorio para todo lo que va aguas abajo.

---

## 2. Flujo interno de `wf-design-intake`

**Pregunta que responde:** ¿como se cierra el `DESIGN_BRIEF.md` antes del sistema visual?

```mermaid
flowchart TD
    Spec[feature_spec.md]
    PRD[prd.md opcional]
    Mood[_design_moodboard.md<br/>opcional]
    Spec --> Check{"Spec valido?"}
    Check -->|No| Stop[Detener]
    Check -->|Si| Existing{"¿Existe ya<br/>DESIGN_BRIEF.md?"}
    Existing -->|Si| Update{"Revisar / sobrescribir / cancelar"}
    Existing -->|No| Detect[Deteccion automatica de preset]
    Update -->|Revisar| Detect
    Update -->|Sobrescribir| Detect
    Spec --> Detect
    PRD --> Detect
    Mood --> Detect
    Detect --> Mode{"guided | hybrid | auto"}
    Mode -->|guided| Tree["Arbol de decision<br/>(kb-design-style-decision-tree)<br/>+ --learn si activo"]
    Mode -->|hybrid| Propose[Proponer defaults<br/>+ pedir confirmacion]
    Mode -->|auto| Infer[Inferir desde spec/PRD/preset<br/>con trazabilidad por variable]
    Tree --> Consistency{Consistencia OK?}
    Propose --> Consistency
    Infer --> Consistency
    Consistency -->|No| Resolve[Resolver conflicto o pedir correccion]
    Resolve --> Consistency
    Consistency -->|Si| Brief[DESIGN_BRIEF.md<br/>+ Update log si actualizado]

    style Mood fill:#e0f7fa,stroke:#00838f
    style Tree fill:#ede7f6,stroke:#5e35b1
    style Brief fill:#fff8e1,stroke:#f9a825
```

**Mensaje clave:** el brief reduce decisiones implicitas y deja trazado quien manda en las ambiguedades del estilo. El intake detecta presets automaticamente desde el contexto del producto, soporta moodboard previo y modo `--learn` para diseñadores junior.

---

## 3. Flujo interno de `wf-design-system`

**Pregunta que responde:** ¿como se genera o actualiza el `DESIGN.md` de producto?

```mermaid
flowchart TD
    Spec[feature_spec.md]
    Brief[DESIGN_BRIEF.md<br/>requerido]
    Spec --> Check{"Spec valido y en sync?"}
    Check -->|No| Stop[Detener]
    Check -->|Si| BriefGate{"¿Existe DESIGN_BRIEF.md?"}
    BriefGate -->|No| StopBrief["Detener: ejecutar wf-design-intake<br/>o reintentar con --no-brief"]
    BriefGate -->|Si| Existing{"¿Ya existe DESIGN.md?"}
    Existing -->|Si| ReadCurrent[Leer DESIGN.md actual]
    Existing -->|No| NewSystem[Crear sistema visual base]
    Brief --> Agent["design-architect<br/>modo design-system"]
    ReadCurrent --> Agent
    NewSystem --> Agent
    Agent --> DesignFile[DESIGN.md]

    style DesignFile fill:#f3e5f5,stroke:#8e24aa
    style Brief fill:#fff8e1,stroke:#f9a825
    style StopBrief fill:#ffebee,stroke:#c62828
```

**Mensaje clave:** `DESIGN.md` es un artefacto de producto persistente y no nace de inferencias libres: el `DESIGN_BRIEF.md` es precondicion obligatoria, salvo override explicito `--no-brief` para casos legacy.

---

## 4. Flujo interno de `wf-design-feature-prototype`

**Pregunta que responde:** ¿como se derivan los artefactos listos para Stitch desde un spec?

```mermaid
flowchart TD
    Spec[feature_spec.md]
    DesignFile[DESIGN.md]
    Brief[DESIGN_BRIEF.md<br/>requerido]
    Spec --> Check{"Spec valido?"}
    Check -->|No| Stop[Detener]
    Check -->|Si| BriefGate{"¿Existe DESIGN_BRIEF.md?"}
    BriefGate -->|No| StopBrief["Detener: ejecutar wf-design-intake<br/>o reintentar con --no-brief"]
    BriefGate -->|Si| Agent["design-architect<br/>modo feature-prototype"]
    DesignFile --> Agent
    Brief --> Agent
    Agent --> Flows["<feature>_flows.md"]
    Agent --> Views["<feature>_views.md"]
    Agent --> Prompt["<feature>_ui_prompt.md"]

    style Flows fill:#ede7f6,stroke:#5e35b1
    style Views fill:#f3e5f5,stroke:#8e24aa
    style Prompt fill:#fce4ec,stroke:#d81b60
    style Brief fill:#fff8e1,stroke:#f9a825
    style StopBrief fill:#ffebee,stroke:#c62828
```

**Mensaje clave:** la fase produce tres artefactos distintos para evitar que todo el contrato visual quede enterrado dentro de un prompt. El brief es precondicion obligatoria: la feature debe heredar la misma policy de autonomia, `clarity_vs_brand` y `accessibility_target` que el sistema visual.

---

## 5. Contrato de artefactos en Design

**Pregunta que responde:** ¿que aporta cada archivo de la fase?

```mermaid
flowchart LR
    subgraph Product["Nivel producto"]
        B["DESIGN_BRIEF.md<br/>direccion, autonomia, tradeoffs"]
        D["DESIGN.md vMAJOR.MINOR.PATCH<br/>tokens, type scale, color modes,<br/>iconografia, motion, voice"]
        BR["DESIGN.&lt;branch&gt;.md<br/>(exploracion paralela)"]
        DA["_delta_analysis.md<br/>(cambios propuestos)"]
        TK["tokens/<br/>(export a CSS/Compose/SwiftUI/...)"]
        A11Y["a11y_audit_&lt;fecha&gt;.md<br/>(report)"]
        FB["&lt;feature&gt;_design_feedback.md /<br/>design_feedback_&lt;fecha&gt;.md"]
    end

    subgraph Feature["Nivel feature"]
        MOOD["_design_moodboard.md<br/>(inspiracion previa)"]
        DISC["_design_discovery.md<br/>(apps de referencia)"]
        F["_flows.md<br/>secuencias y transiciones"]
        V["_views.md<br/>pantallas, componentes, estados,<br/>microcopy"]
        P["_ui_prompt.md<br/>ensamblaje para Stitch"]
        VAR["_variants.md<br/>(A/B con hipotesis)"]
    end

    B --> D
    MOOD --> B
    DISC --> D
    D --> F
    D --> V
    F --> P
    V --> P
    D -.iterar.-> DA
    DA -.aplicar.-> D
    D -.explorar.-> BR
    BR -.merge.-> D
    D --> TK
    D --> A11Y
    V -.A/B.-> VAR
    FB -.triage.-> B
    FB -.triage.-> DA

    style B fill:#fff8e1,stroke:#f9a825
    style D fill:#f3e5f5,stroke:#8e24aa
    style BR fill:#fff3e0,stroke:#fb8c00
    style DA fill:#ede7f6,stroke:#5e35b1
    style TK fill:#e8f5e9,stroke:#43a047
    style A11Y fill:#ede7f6,stroke:#5e35b1
    style FB fill:#fce4ec,stroke:#d81b60
    style MOOD fill:#e0f7fa,stroke:#00838f
    style DISC fill:#e0f7fa,stroke:#00838f
    style VAR fill:#fff3e0,stroke:#fb8c00
```

**Mensaje clave:** los artefactos a nivel **producto** capturan identidad persistente (brief, sistema visual versionado, tokens exportables, auditorias). Los artefactos a nivel **feature** materializan esa identidad en pantallas concretas y permiten experimentar (variantes, A/B). El feedback de stakeholders se canaliza siempre via captura + triage hacia el workflow apropiado.

---

## 6. Handoff desde Design hacia Stitch y Plan

**Pregunta que responde:** ¿como se usa la salida de design despues de generarla?

```mermaid
flowchart TD
    Design["DESIGN.md + DESIGN_BRIEF.md"]
    Bundle["flows / views / ui_prompt<br/>(por feature)"]
    Export["wf-design-export"]
    Tokens["tokens/ (CSS, Compose, SwiftUI,<br/>Style Dictionary, Tailwind)"]
    A11y["wf-design-a11y-audit"]
    A11yReport["a11y_audit_&lt;fecha&gt;.md"]
    Stitch["Stitch / Figma"]
    Review{"¿Validado con cliente?"}
    Feedback["wf-design-feedback capture"]
    Triage["wf-design-feedback triage"]
    Iterate{"Categoria del feedback"}
    BackToBrief["wf-design-intake<br/>(brief_change)"]
    BackToDelta["wf-design-delta<br/>(design_delta)"]
    BackToView["regenerar views<br/>(feature_view_change)"]
    BackToSpec["wf-spec-delta<br/>(functional_change)"]
    Plan["wf-prepare-plan<br/>sobre feature_spec.md"]

    Design --> Bundle
    Design --> Export
    Export --> Tokens
    Design --> A11y
    A11y --> A11yReport
    Bundle --> Stitch
    Design --> Stitch
    Stitch --> Review
    Review -->|No| Feedback
    Feedback --> Triage
    Triage --> Iterate
    Iterate -->|brief_change| BackToBrief
    Iterate -->|design_delta| BackToDelta
    Iterate -->|feature_view_change| BackToView
    Iterate -->|functional_change| BackToSpec
    BackToBrief -.regenera.-> Design
    BackToDelta -.regenera.-> Design
    BackToView -.regenera.-> Bundle
    Review -->|Si| Plan
    Tokens --> Plan
    A11yReport -.cumple.-> Plan

    style Stitch fill:#e3f2fd,stroke:#1976d2
    style Plan fill:#e8f5e9,stroke:#388e3c
    style Tokens fill:#e8f5e9,stroke:#43a047
    style Feedback fill:#fce4ec,stroke:#d81b60
    style Triage fill:#fce4ec,stroke:#d81b60
    style A11y fill:#ede7f6,stroke:#5e35b1
    style A11yReport fill:#ede7f6,stroke:#5e35b1
```

**Mensaje clave:** el handoff a `plan` no es un dump del DESIGN.md: requiere tokens exportables (`wf-design-export`), validacion a11y ejecutiva (`wf-design-a11y-audit`) y procesado estructurado del feedback de cliente via captura + triage hacia el workflow correcto. El plan no nace del mockup, sino del spec con el contrato visual validado y los tokens listos para codigo.

---

## 7. Ciclo de auditoria y evolucion del sistema visual

**Pregunta que responde:** ¿como se mantiene `DESIGN.md` saludable a lo largo del tiempo?

```mermaid
flowchart TD
    Design[DESIGN.md existente]
    Brief[DESIGN_BRIEF.md]

    Design --> Validate["wf-design-validate"]
    Brief --> Validate
    Validate --> Status{"Resultado"}
    Status -->|PASS| OK[Sin accion]
    Status -->|PASS_WITH_GAPS| Delta1["wf-design-delta analyze"]
    Status -->|FAIL| Decide{"¿Es estructural?"}
    Decide -->|Si| Regen["wf-design-system<br/>regenerar"]
    Decide -->|No| Delta1

    NewReqs[Nuevos requisitos visuales] --> Delta1
    Delta1 --> Analysis["_delta_analysis.md"]
    Analysis --> Review{"¿Aprobado por usuario?"}
    Review -->|No| Iterate[Ajustar analysis]
    Iterate --> Review
    Review -->|Si| Delta2["wf-design-delta apply"]
    Delta2 --> DesignUpdated["DESIGN.md<br/>+ Changelog"]

    BriefChange{"¿Toca style_family<br/>o clarity_vs_brand?"}
    Delta1 --> BriefChange
    BriefChange -->|Si| Intake["wf-design-intake<br/>actualizar brief primero"]
    Intake --> Brief

    style Validate fill:#ede7f6,stroke:#5e35b1
    style Delta1 fill:#ede7f6,stroke:#5e35b1
    style Delta2 fill:#ede7f6,stroke:#5e35b1
    style DesignUpdated fill:#f3e5f5,stroke:#8e24aa
    style Brief fill:#fff8e1,stroke:#f9a825
    style Regen fill:#fff3e0,stroke:#f57c00
```

**Mensaje clave:** `wf-design-validate` detecta gaps sin escribir; `wf-design-delta` los aplica preservando lo previo y dejando rastro en `## Changelog` con bump de version semver. Las mutaciones que tocan `style_family` o `clarity_vs_brand` son cambios de brief — pasan primero por `wf-design-intake`.

---

## 8. Exploracion paralela y A/B testing

**Pregunta que responde:** ¿como se prueban hipotesis visuales sin romper production?

```mermaid
flowchart TD
    Design["DESIGN.md (main)"]

    subgraph Branching["Exploracion del sistema visual completo"]
        BranchCreate["wf-design-branch create &lt;name&gt;"]
        BranchFile["DESIGN.&lt;branch&gt;.md"]
        BranchIterate["Iterar (delta sobre el branch)"]
        BranchCompare["wf-design-branch compare"]
        BranchDecision{"Decision"}
        BranchMerge["wf-design-branch merge --into main<br/>(bump semver segun cambio)"]
        BranchDiscard["wf-design-branch discard"]
    end

    subgraph Variants["A/B testing por feature"]
        VariantCreate["wf-design-variant create<br/>--variants A,B --hypothesis"]
        VariantFiles["_views.A.md / _views.B.md<br/>_flows.A.md / _flows.B.md"]
        VariantsDoc["_variants.md<br/>(hipotesis + metrica)"]
        Validate["Validar en produccion<br/>(usando Success Metrics del brief)"]
        VariantCompare["wf-design-variant compare"]
        Winner{"¿Ganador?"}
        ApplyWinner["wf-design-delta<br/>aplicar variante ganadora"]
        Iterate["Iterar nuevas variantes"]
    end

    Design --> BranchCreate
    BranchCreate --> BranchFile
    BranchFile --> BranchIterate
    BranchIterate --> BranchCompare
    BranchCompare --> BranchDecision
    BranchDecision -->|merge| BranchMerge
    BranchDecision -->|descartar| BranchDiscard
    BranchMerge --> Design

    Design --> VariantCreate
    VariantCreate --> VariantFiles
    VariantCreate --> VariantsDoc
    VariantFiles --> Validate
    Validate --> VariantCompare
    VariantCompare --> Winner
    Winner -->|si| ApplyWinner
    Winner -->|no concluyente| Iterate
    ApplyWinner --> Design

    style Design fill:#f3e5f5,stroke:#8e24aa
    style BranchFile fill:#fff3e0,stroke:#fb8c00
    style BranchMerge fill:#fff3e0,stroke:#fb8c00
    style BranchDiscard fill:#ffebee,stroke:#c62828
    style VariantsDoc fill:#fff3e0,stroke:#fb8c00
    style ApplyWinner fill:#ede7f6,stroke:#5e35b1
```

**Mensaje clave:** `wf-design-branch` opera a nivel **sistema** (probar otra direccion visual completa); `wf-design-variant` opera a nivel **feature** (probar dos versiones de la misma pantalla con metrica). Ninguno toca `DESIGN.md` principal hasta que se decide merge o aplicar ganador. Las exploraciones que terminan sin merge se descartan limpiamente.

---

## 9. Loop de feedback de stakeholders

**Pregunta que responde:** ¿como se incorpora el feedback no estructurado (cliente, PM, dev, QA) sin perder trazabilidad?

```mermaid
flowchart TD
    Stakeholder["Cliente / PM / Dev / QA / Stitch"]
    Capture["wf-design-feedback capture<br/>(literal, sin reformular)"]
    File["&lt;feature&gt;_design_feedback.md /<br/>design_feedback_&lt;fecha&gt;.md<br/>status: pending_triage"]
    Triage["wf-design-feedback triage<br/>(design-architect razona)"]
    Triaged["&lt;feature&gt;_design_feedback.md /<br/>design_feedback_&lt;fecha&gt;.md<br/>status: triaged"]

    Cats{"Categoria por item"}
    Brief["brief_change<br/>→ wf-design-intake"]
    Delta["design_delta<br/>→ wf-design-delta"]
    View["feature_view_change<br/>→ regenerar views"]
    Copy["microcopy_change<br/>→ actualizar microcopy"]
    A11y["a11y_concern<br/>→ wf-design-a11y-audit"]
    Func["functional_change<br/>→ wf-spec-delta"]
    OOS["out_of_scope<br/>→ documentar + descartar"]

    Stakeholder --> Capture
    Capture --> File
    File --> Triage
    Triage --> Triaged
    Triaged --> Cats
    Cats --> Brief
    Cats --> Delta
    Cats --> View
    Cats --> Copy
    Cats --> A11y
    Cats --> Func
    Cats --> OOS

    style Capture fill:#fce4ec,stroke:#d81b60
    style Triage fill:#fce4ec,stroke:#d81b60
    style Brief fill:#fff8e1,stroke:#f9a825
    style Delta fill:#ede7f6,stroke:#5e35b1
    style A11y fill:#ede7f6,stroke:#5e35b1
    style Func fill:#fff3e0,stroke:#f57c00
    style OOS fill:#ffebee,stroke:#c62828
```

**Mensaje clave:** el feedback se captura literal y se triajea en una de siete categorias accionables. Cada categoria activa el workflow correcto. Esto evita el patron "el cliente dijo algo y nadie sabe que hacer con ello": queda traza del feedback original, del triage y del workflow que lo aplico.
