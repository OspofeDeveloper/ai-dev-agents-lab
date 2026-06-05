# Plantillas de inventario del ecosistema SDD

## Formato del snapshot (Paso 6)

```
# SDD Ecosystem Status
Fecha: <fecha>
Alcance: <fase o global>

## Resumen
- Skills totales: X (Y kb-*, Z wf-*)
- Agentes totales: N
- KBs sin consumidor: M
- Workflows sin registrar en rootmap: P

## Por fase

### <fase> (o meta para meta-ecosistema)
Agentes (N):
  - <nombre> — <primera linea de description>

kb-* (Y):
  - <nombre> — <primera linea de description>

wf-* (Z):
  - <nombre> [SIN REGISTRAR?] — <primera linea de description>

### tech/<stack>
  [misma estructura]

## KBs sin consumidor
  - <path> — <nombre>

## Workflows sin registrar en rootmap
  - <path> — <nombre>
```

## Formato del skill-registry (Paso 6.5)

El formato del registry vive en el generador determinista `sdd/scripts/generate-skill-registry.py` (SSoT de generación). El Paso 6.5 ejecuta ese script; no existe plantilla manual del registry para evitar una segunda fuente de verdad.
