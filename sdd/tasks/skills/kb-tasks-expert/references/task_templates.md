# Templates de Task por Dominio de Ejecución (genérico)

Usa estos templates para formatear cada Task en el `_tasks.md`. Sustituye los valores `[EN CORCHETES]`. En proyectos con overlay de stack, la variante especializada de esta KB sustituye estos templates por los suyos.

---

## Template: Task de implementación (universal)

```markdown
## T-00X: [Dominio de ejecución] — [Nombre del componente]

- **Spec CA:** [CA-XXX | —]
- **Plan ref:** [§Sección del Plan que define este componente]
- **Ubicación:** [ruta/real/en/el/repositorio]
- **Execution domain:** [contrato | implementación | integración | superficie | infraestructura]
- **Owner agent:** orquestador
- **Suggested workflow:** [wf-* aplicable | —]
- **Input:** [síntesis de lo que la task necesita del Plan y de tasks anteriores]
- **Dependencies:** [T-00Y, ... | ninguna]
- **Definition of done:** [artefactos concretos que deben existir, con sus rutas, y condición verificable de completitud]
```

Reglas de relleno:

- **Ubicación** siempre es una ruta real del repositorio (existente o a crear), nunca un módulo abstracto que el repo no tiene.
- **Execution domain** clasifica la naturaleza del cambio, no la tecnología: `contrato` (interfaces, modelos, esquemas), `implementación` (lógica que cumple un contrato), `integración` (wiring, registro, conexión entre piezas), `superficie` (UI, CLI, API pública, docs de uso), `infraestructura` (build, config, tooling transversal).
- **Owner agent** en modo genérico es siempre `orquestador` (Claude implementa la task directamente, en orden, validando la definition of done antes de pasar a la siguiente).
- **Definition of done** debe ser verificable leyendo el repo: archivos que existen, comandos que pasan, comportamiento observable.

---

## Template: Task de scaffold / preparación (T-000)

Primera task cuando el Plan requiere estructura previa:

```markdown
## T-000: Infraestructura — [Estructura base de la feature]

- **Spec CA:** —
- **Plan ref:** §Estructura técnica
- **Ubicación:** [directorios/rutas a crear]
- **Execution domain:** infraestructura
- **Owner agent:** orquestador
- **Suggested workflow:** —
- **Input:** Estructura definida en el Plan: [síntesis]
- **Dependencies:** ninguna
- **Definition of done:** Estructura base creada y preparada para las tasks posteriores.
```

---

## Template: Task de tests

Una task de tests acompaña a cada bloque de implementación que valida (no todas al final del todo, salvo que el Plan no defina testing y se agrupen al cierre):

```markdown
## T-00X: Tests — [Componente que validan]

- **Spec CA:** [CA-XXX que el test demuestra]
- **Plan ref:** [§Sección]
- **Ubicación:** [ruta de la suite de tests]
- **Execution domain:** implementación
- **Owner agent:** orquestador
- **Suggested workflow:** —
- **Input:** [casos: happy path, errores, edge cases derivados de los CAs]
- **Dependencies:** [T-00Y (componente bajo test)]
- **Definition of done:** Suite creada y pasando con el runner del proyecto: `[comando real]`.
```
