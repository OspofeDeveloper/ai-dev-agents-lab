# Test 06 — `check-conflicts`

**Propósito del workflow:** Detectar conflictos entre specs de features ya existentes (HUs duplicadas, CAs contradictorios, scope overlap, shared models inconsistentes, fuera de alcance contradictorio). Puede ejecutarse tras `decompose-spec` o de forma independiente.

---

## Prompt de activación

Revisar conflictos de una feature concreta contra el resto:
```
/check-conflicts sdd/features/hogar_spec.md --features-dir sdd/features/
```

Revisar todas las features entre sí:
```
/check-conflicts --features-dir sdd/features/
```

---

## Flujo esperado paso a paso

### Paso 1 — El orquestador L1 parsea el comando
**Actor:** skill `check-conflicts` (L1)
**Acción:** Determina el scope del análisis:
- Si se pasa un spec concreto: ese spec vs todos los demás en `--features-dir`
- Si solo se pasa `--features-dir`: todas las features entre sí (N×N comparaciones)
**Verifica precondiciones:**
- Los archivos/directorio existen
- Hay al menos 2 specs para comparar (si solo hay 1, no tiene sentido)

**Señal de correcto:** El agente confirma qué specs va a comparar antes de lanzar el subagente.

---

### Paso 2 — El orquestador lanza el subagente `sdd-analyst`
**Actor:** skill `check-conflicts` (L1)
**Acción:** Invoca `Agent(subagent_type="sdd-analyst")` con:
```
modo: conflict
specs: [<contenido spec A>, <contenido spec B>, ...]
```

---

### Paso 3 — El subagente `sdd-analyst` enruta al workflow correcto
**Actor:** agente `sdd-analyst` (L2)
**Carga como contexto:**
- Knowledge `spec-expert` — para entender la estructura de los specs
- Knowledge `conflict-expert` — las 5 reglas de detección + severidades
- Workflow `spec-conflict` — instrucciones paso a paso

---

### Paso 4 — El subagente ejecuta el workflow `spec-conflict`
**Actor:** agente `sdd-analyst` (L2), guiado por `spec-conflict` (L3)
**Acciones en orden:**

Para cada par de features (A, B):

**Regla 1 — HUs duplicadas:**
- Mismo actor + misma acción + mismo objetivo → conflicto ALTA severidad

**Regla 2 — CAs contradictorios:**
- Mismo GIVEN + mismo WHEN + THEN incompatible entre sí → conflicto ALTA severidad

**Regla 3 — Scope overlap:**
- El Journey de A incluye el objetivo central de B → conflicto MEDIA severidad

**Regla 4 — Shared models inconsistentes:**
- El mismo modelo aparece en A y B con atributos o comportamientos distintos → conflicto ALTA severidad
- (Esto debería haberse evitado en decompose, pero puede pasar en fast-track)

**Regla 5 — Fuera de alcance contradictorio:**
- Algo declarado "fuera de alcance" en A está dentro del alcance de B → conflicto MEDIA severidad

Para cada conflicto encontrado, registra:
- ID: `CONF-001`, `CONF-002`, etc.
- Regla disparada
- Features involucradas
- Fragmento exacto de cada spec que genera el conflicto
- Severidad: ALTA / MEDIA
- Sugerencia de resolución

**Señal de correcto:** Los conflictos citan el fragmento exacto del spec (no son genéricos) y proponen una resolución concreta.

---

### Paso 5 — El subagente escribe el artefacto de salida
**Actor:** agente `sdd-analyst` (L2)
**Si hay conflictos:** Genera el archivo en el directorio de features:
- `features/_conflict_report.md` (o en el dir del spec si fue una revisión puntual)

**Si no hay conflictos:** Lo indica solo en el chat — no genera archivo.

**Contenido del conflict report:**
```
# Conflict Report
Generado: [fecha]
Features analizadas: [lista]

## CONF-001 [ALTA] — HU duplicada
- Feature A: HU-003 "Como cuidador, quiero ver el histórico..."
- Feature B: HU-007 "Como cuidador, quiero consultar el historial..."
- Regla: HUs duplicadas (mismo actor + acción + objetivo)
- Sugerencia: Consolidar en Feature A, eliminar HU-007 de Feature B

## CONF-002 [MEDIA] — Scope overlap
...
```

---

## Resultado esperado

| Elemento | Valor |
|----------|-------|
| Archivo generado | `_conflict_report.md` (solo si hay conflictos) |
| Sin conflictos | Solo mensaje inline confirmando que no hay conflictos |
| Bloqueo | No bloquea — el report es informativo |
| Siguiente paso | Corregir los specs afectados (manualmente) antes de pasar a plan |

---

## Señales de fallo (qué validar)

- El agente genera un conflict report vacío cuando hay conflictos evidentes
- Los conflictos no citan el fragmento exacto (son genéricos)
- No distingue entre severidad ALTA y MEDIA
- Genera conflictos falsos (ruido) donde no los hay
- No cubre las 5 reglas — omite alguna (p.ej. solo busca HUs duplicadas)
- Genera el archivo de conflict report aunque no haya conflictos
