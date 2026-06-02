# Guía de referencia para wf-design-intake

## Heurística de detección automática de preset (Paso 7)

| Contexto del producto | Preset sugerido |
|---|---|
| B2B / dashboard / backoffice / herramienta de trabajo | `b2b-operational` |
| Fintech / banca / pagos / regulado financiero | `fintech-trust` |
| Salud / mindfulness / wellness / bienestar | `health-calm` |
| Consumer / lifestyle / social / fitness / engagement | `consumer-lifestyle` |
| Media / lectura / contenido curado / luxury | `content-editorial` |

Comportamiento por modo:
- **`auto`**: aplica el preset detectado sin preguntar. Marca `product_preset` como `inferred`.
- **`hybrid`**: propón el preset detectado y pide confirmación: `"Detecte que este producto encaja con el preset <X> por <razon corta>. ¿Confirmar o cambiar?"`
- **`guided`**: muestra los presets disponibles y pide elección explícita.

Si se pasa `--preset` en CLI, respeta esa elección y omite la detección.

Al aplicar un preset:
- Carga defaults de `${CLAUDE_SKILL_DIR}/../kb-design-brief/references/design_presets.md`
- Usa esos defaults como base y ajusta solo lo que contradiga al producto real
- Documenta en el brief: `product_preset` y `source: preset|user|inferred`

Si ningún preset encaja, usa `none` y decide campo a campo.

## Trazabilidad en modo auto (Paso 6)

Por cada variable cerrada en modo `auto`, registrar la fuente de la inferencia en la sección `## Inferencias automaticas` del brief:

| Variable | Valor | Fuente |
|---|---|---|
| `style_family` | `productive-minimal` | `spec` |

Fuentes válidas: `spec`, `PRD`, `preset`, `inferred` (deducida por heurística sin fuente directa).

Esta tabla permite al usuario auditar y revertir variables mal inferidas.
