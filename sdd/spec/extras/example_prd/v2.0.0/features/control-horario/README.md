# Control Horario

> **Feature ID**: F-004
> **Spec**: control-horario_spec.md
> **Actor principal**: Trabajadora SAD
> **PRD origen**: prd-hogar-sad.md

## Descripcion

Fichaje de entrada/salida con geolocalizacion y consulta de historial de fichajes por servicio.

## Shared Models

| Rol | Modelo | Descripcion |
|-----|--------|-------------|
| Owner | RegistroFichaje | Esta feature crea y gestiona los registros de fichaje |
| Referencia | Servicio | Owner: F-003 — Gestion de Servicios |

## Artefactos

| Etapa | Archivo | Estado |
|-------|---------|--------|
| Spec | control-horario_spec.md | Done |
| Plan | control-horario_plan.md | — |
| Tasks | control-horario_tasks.md | — |

## Dependencias

- **Requiere**: F-001 (Autenticacion), F-003 (Gestion de Servicios — lista de servicios activos)
- **Bloquea**: Ninguna
