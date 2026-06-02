# Instrucción de comparación para el agente design-architect

Incluir en el prompt del agente para modo `compare`:

```text
INSTRUCCION: produce un comparativo estructurado (semantic diff, no diff literal):

## Diferencias en visual_personality
- <campo>: A=<valor> vs B=<valor>

## Diferencias en colors
- <token>: A=<valor> vs B=<valor> (en modo light/dark)

## Diferencias en typography
- <rol>: A=<...> vs B=<...>

## Diferencias en components
- <componente>: estados anadidos/quitados/cambiados

## Diferencias en motion / iconography / layout

## Diferencias en voice & microcopy

## Resumen
- Cuantos tokens difieren
- Severidad del diff (cosmetic / structural / breaking)
- Recomendacion: merge directo, requiere triage, no fusionable

No reescribas archivos. Solo compara.
```
