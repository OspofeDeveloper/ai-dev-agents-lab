# Test 04 — `wf-spec-fast-track`

**Propósito del workflow:** Generar directamente el spec de una feature concreta sin necesidad de spec monolítico previo. Atajo para features pequeñas o aisladas donde no hay un PRD completo del que partir.

---

## Prompt de activación

```
/wf-spec-fast-track sdd/prd-hogar-sad.md --capability notificaciones-push
```

Variante con descripción libre en vez de nombre de capability:
```
/wf-spec-fast-track sdd/prd-hogar-sad.md --capability "gestión de cuidadores"
```

O si el documento es específico de esa feature:
```
/wf-spec-fast-track sdd/requisitos-notificaciones.md
```

---

## Flujo esperado paso a paso

### Paso 1 — El orquestador L1 parsea el comando
**Actor:** skill `wf-spec-fast-track` (L1)
**Acción:** Lee el path del documento y (si existe) el flag `--capability`.
**Verifica precondiciones:**
- El archivo existe
- Si `--capability` está presente, lo extrae como scope de la feature
- Si no hay `--capability`, intenta inferir la feature del propio documento

**Señal de correcto:** El agente identifica claramente el scope de la feature antes de lanzar el subagente.

---

### Paso 2 — El orquestador lanza el subagente `sdd-analyst`
**Actor:** skill `wf-spec-fast-track` (L1)
**Acción:** Invoca `Agent(subagent_type="sdd-analyst")` con:
```
modo: fast-track
documento: <contenido del documento>
capability: "notificaciones-push"  (si se especificó)
```

---

### Paso 3 — El subagente `sdd-analyst` enruta al workflow correcto
**Actor:** agente `sdd-analyst` (L2)
**Carga como contexto:**
- Knowledge `kb-spec-expert` — reglas de los 8 elementos SDD
- Knowledge `kb-decompose-expert` — para generar spec autocontenido de feature (sin spec monolítico padre)
- Knowledge `kb-gap-conventions` — para marcar gaps si los hay
- Workflow `wf-spec-fast-track` — instrucciones para este modo

**Diferencia clave vs finalize:** Aquí se genera un spec de feature (autocontenido), no un spec monolítico.

---

### Paso 4 — El subagente ejecuta el workflow `wf-spec-fast-track`
**Actor:** agente `sdd-analyst` (L2), guiado por `wf-spec-fast-track` (L3)
**Acciones en orden:**
1. Delimita el scope de la feature (usa `--capability` o infiere del documento)
2. Genera el spec de la feature con los 8 elementos SDD, aplicando la Prueba de Pureza
3. Como es una feature aislada:
   - Los shared models se declaran como "propios de esta feature" (no hay otras features con las que coordinar)
   - Los actores son los del scope de esta feature
4. Si hay gaps de información:
   - CRÍTICO: bloquea y lista las preguntas
   - INFORMATIVO: aplica asunción por defecto y lo indica
5. Genera también el `README.md` de la feature (visión general)

**Señal de correcto:** El spec generado es autocontenido — puede leerse sin necesidad de ningún otro documento.

---

### Paso 5 — El subagente escribe los artefactos de salida
**Actor:** agente `sdd-analyst` (L2)
**Acción:** Genera los archivos en la ruta `features/<nombre-feature>/`:
- `features/notificaciones-push/notificaciones-push_spec.md`
- `features/notificaciones-push/README.md`

**Señal de correcto:** La carpeta de la feature se crea automáticamente, el nombre deriva del `--capability` o del nombre inferido.

---

## Resultado esperado

| Elemento | Valor |
|----------|-------|
| Archivos generados | `features/<nombre>/<nombre>_spec.md` y `features/<nombre>/README.md` |
| Artefacto | Spec de feature autocontenido con los 8 elementos SDD |
| Bloqueo | Si hay gaps CRÍTICO en el documento fuente |
| Siguiente paso | `/wf-prepare-plan features/<nombre>/<nombre>_spec.md` directamente |

---

## Diferencia clave con `finalize`

| Aspecto | `finalize` | `fast-track` |
|---------|-----------|--------------|
| Origen | PRD completo | Cualquier documento |
| Salida | `prd_spec.md` monolítico | `features/X/X_spec.md` de feature |
| Requiere `analyze` previo | Recomendado | No |
| Requiere `decompose` posterior | Sí | No |

---

## Señales de fallo (qué validar)

- Genera `prd_spec.md` en vez de un spec de feature
- No crea la carpeta `features/<nombre>/`
- El spec no es autocontenido (hace referencia a un spec padre que no existe)
- No genera el `README.md` de la feature
- Ignora el `--capability` y toma todo el documento como scope
