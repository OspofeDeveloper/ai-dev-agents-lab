# SDD PRD — Diagramas de la fase de entrada

Este documento contiene los diagramas detallados de la fase `prd`: entrada de requisitos, preflight y gobernanza de cambios de producto.

Para la vista global del sistema, usa [sdd/DIAGRAMS.md](/Users/oscar/Documents/GitHub/ai-dev-agents-lab/sdd/DIAGRAMS.md).

---

## 1. Entrada PRD antes de entrar en Spec

**Pregunta que responde:** ¿qué ocurre desde un brief informal hasta tener un PRD listo para `spec`?

```mermaid
flowchart TD
    Notes[Notas / brief / discovery humano]
    Notes -->|"wf-prd-create"| Draft[PRD.md inicial]
    Draft -->|"wf-prd-review"| Review{PRD procesable?}
    Review -->|No| Fix[Reescribir negocio, actores, alcance]
    Fix --> Draft
    Review -->|Si| Ready[PRD listo para wf-spec-analyze]

    style Draft fill:#e3f2fd,stroke:#1976d2
    style Ready fill:#e8f5e9,stroke:#388e3c
    style Fix fill:#fff3e0,stroke:#f57c00
```

**Mensaje clave:** `wf-prd-review` no crea specs; solo evita que entre a `spec` un PRD contaminado o mal planteado.

---

## 2. Gobernanza: aclaracion vs cambio de producto

**Pregunta que responde:** cuando aparece nueva informacion, ¿basta con resolver un gap o hay que abrir un change request?

```mermaid
flowchart TD
    Q{"La nueva informacion..."}
    Q -->|"aclara algo ya comprometido"| Clarification[CLARIFICATION]
    Q -->|"cambia alcance, prioridad o comportamiento"| Change[CHANGE REQUEST]

    Clarification --> Gap["No reescribe PRD<br/>seguir en analysis/spec"]
    Change --> PRDUpdate["Actualizar PRD primero<br/>con wf-prd-change"]

    style Gap fill:#e8f5e9,stroke:#388e3c
    style PRDUpdate fill:#ffebee,stroke:#c62828
```

**Mensaje clave:** si cambia el producto comprometido, el PRD se actualiza antes de tocar derivados.

---

## 3. Flujo interno de `wf-prd-change`

**Pregunta que responde:** ¿qué artefactos produce y qué paso viene después de un cambio de producto?

```mermaid
flowchart TD
    Input["PRD.md + cambio.md"]
    Input --> Classify["Clasificar cambio<br/>clarification / behavior / scope / priority / deprecation"]
    Classify --> Decision{"¿Exige editar PRD?"}
    Decision -->|No| RecordOnly["Registrar cambio sin reescribir PRD"]
    Decision -->|Si| UpdatePRD["Actualizar PRD.md"]
    RecordOnly --> Changelog["product-changelog.md"]
    UpdatePRD --> Changelog
    Changelog --> CRFolder["changes/CR-XXX/<br/>change-request.md + decision.md"]
    CRFolder --> Impact["Siguiente paso:<br/>wf-prd-sync-impact"]

    style UpdatePRD fill:#e3f2fd,stroke:#1976d2
    style CRFolder fill:#fff3e0,stroke:#f57c00
    style Impact fill:#e8f5e9,stroke:#388e3c
```

**Mensaje clave:** `wf-prd-change` no termina en el PRD; deja trazabilidad y prepara la resincronizacion aguas abajo.

---

## 4. Posicion de PRD dentro del pipeline

**Pregunta que responde:** ¿cómo se conecta `prd` con el resto del sistema?

```mermaid
flowchart LR
    PRD["PRD.md"]
    ANALYZE["wf-spec-analyze"]
    SPEC["spec"]
    DESIGN["design"]
    PLAN["plan"]

    PRD --> ANALYZE --> SPEC --> DESIGN --> PLAN
    PRD -.->|"si cambia el producto"| Change["wf-prd-change"]
    Change -.->|"medir desincronizacion"| Sync["wf-prd-sync-impact"]
    Sync -.-> SPEC
    Sync -.-> DESIGN
    Sync -.-> PLAN

    style PRD fill:#e3f2fd,stroke:#1976d2
    style Change fill:#ffebee,stroke:#c62828
```

**Mensaje clave:** PRD es fuente de verdad de negocio incluso despues de haber generado specs.
