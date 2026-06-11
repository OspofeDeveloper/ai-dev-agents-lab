---
name: kb-sdd-audit-structural
description: "Criterios para detectar problemas estructurales del ecosistema SDD: referencias rotas, skills huerfanas, rootmap invalido y agentes con KBs inexistentes, con su severidad. No cubre calidad de contenido (kb-sdd-audit-content) ni reglas de arquitectura (kb-sdd-skill-architecture)."
effort: low
allowed-tools: [Read]
user-invocable: false
---

# KB SDD Audit Structural

Criterios para determinar si el ecosistema SDD es estructuralmente consistente. Un ecosistema estructuralmente valido es aquel donde todas las referencias entre piezas son resolvibles y no hay piezas sin consumidor.

## Que constituye una referencia valida

### En un agente (`.md` en `agents/`)

- Cada nombre en `skills: [...]` debe corresponder a un `SKILL.md` con ese `name:` en el ecosistema.
- El `name:` del frontmatter del agente debe coincidir con el nombre de archivo (sin extension).

### En una `wf-*`

- Si declara `agent: <nombre>`, debe existir un archivo `<nombre>.md` en el directorio `agents/` al mismo nivel que `skills/` dentro de la misma rama.
- El `name:` del frontmatter debe coincidir con el nombre del directorio que contiene el `SKILL.md`.

### En un `CLAUDE.md` (rootmap)

- Cada entrada de la tabla rootmap que referencia un skill (`/wf-<nombre>` o `kb-<nombre>`) debe corresponder a un `SKILL.md` con ese `name:` en el ecosistema.

## Criterios de hallazgo estructural

### [ROTO] Referencias no resolvibles

Un hallazgo `[ROTO]` se produce cuando:

- Un agente lista en `skills: [...]` una KB que no existe fisicamente.
- Una `wf-*` declara `agent: <nombre>` y ese agente no existe en el directorio `agents/` esperado.
- Una entrada de rootmap en un `CLAUDE.md` apunta a un workflow o KB que no existe.

Severidad: **bloqueante**. Una pieza con referencia rota no puede funcionar correctamente.

### [HUERFANA] Skill sin consumidor

Una skill `kb-*` esta huerfana cuando:

- Ningun agente en el ecosistema la lista en su `skills: [...]`.
- No aparece referenciada desde ningun `CLAUDE.md` ni documentacion de fase.

Severidad: **advertencia**. Puede ser una KB nueva pendiente de conectar, o una KB obsoleta que deberia eliminarse.

Una `wf-*` nunca es huerfana por definicion: su consumidor es el usuario final via el rootmap.

### [DESREGISTRADA] Workflow sin entrada en rootmap

Una `wf-*` con `user-invocable: true` que no aparece en ningun rootmap de `CLAUDE.md`.

Severidad: **advertencia**. El workflow existe pero no es descubrible para el orquestador.

### [NOMBRE-DESINCRONIZADO] Nombre de frontmatter distinto al nombre de directorio o archivo

- Una `wf-*` cuyo `name:` en frontmatter no coincide con el nombre del directorio padre del `SKILL.md`.
- Un agente cuyo `name:` no coincide con el nombre del archivo `.md`.

Severidad: **advertencia**. El sistema puede no resolverlo correctamente.

## Alcance del escaneo estructural

El escaneo debe cubrir:

```
sdd/
  <fase>/agents/*.md
  <fase>/skills/*/SKILL.md
  <fase>/CLAUDE.md
  meta/agents/*.md
  meta/skills/*/SKILL.md
  meta/CLAUDE.md
  tech/<stack>/agents/*.md
  tech/<stack>/skills/**/SKILL.md
```

## Formato de reporte estructural

Por cada hallazgo:

```
[SEVERIDAD] <tipo>
Archivo: <path>
Referencia: <nombre no resolvible o elemento faltante>
Descripcion: <una linea explicando el problema>
Accion sugerida: <correccion concreta>
```

Al final del reporte:
- Total de hallazgos por severidad
- Lista de skills huerfanas si las hay
- Estado global: `CONSISTENTE` / `INCONSISTENTE`
