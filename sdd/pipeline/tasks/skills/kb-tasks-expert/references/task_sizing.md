# Reglas de Granularidad de Tasks

---

## Principio fundamental

> Una Task debe poder ser completada por un único owner y producir artefactos coherentes con el resto del proyecto.

---

## Tamaño correcto por tipo de componente

| Componente | Tamaño recomendado | Notas |
|---|---|---|
| Scaffold o preparación estructural | 1 Task por feature o bloque estructural | Siempre T-000 si el Plan la requiere |
| Un contrato (interfaz, modelo, esquema) | 1 Task (puede agrupar contratos relacionados simples) | Si son entidades independientes → Tasks separadas |
| Una implementación de contrato | 1 Task | Puede dividirse si depende de varias piezas externas |
| Una pieza de integración (wiring, registro, conexión) | 1 Task | No mezclar con la implementación que conecta |
| Una superficie (pantalla, comando CLI, endpoint, doc de uso) | 1 Task | Separada de la lógica que presenta |
| Infraestructura transversal (build, config, tooling) | 1 Task por pieza | Si sirve a varias features, va antes que ellas |
| Tests de un componente | 1 Task | Happy path + errores + edge cases del componente |

---

## Señales de que una Task es demasiado grande

- La descripción contiene "y también" o "además"
- El campo `Input` menciona más de 2 entidades de negocio distintas
- La `Definition of done` lista más de 6 artefactos significativos
- La Task mezcla dos dominios de ejecución sin relación de dependencia directa

**Solución:** divide en dos Tasks con dependencia explícita.

---

## Señales de que una Task es demasiado pequeña

- La Task solo crea un archivo de menos de 10 líneas reales
- La Task no puede validarse ni tener valor sin otra Task inmediata e inseparable

**Solución:** agrupa con la Task relacionada.

---

## Definition of Done por tipo de componente

| Tipo | Artefactos que deben existir al completar |
|---|---|
| Scaffold | Estructura de directorios/config base creada y referenciada por el Plan |
| Contrato | Archivo(s) del contrato en la ruta definida — sin lógica de implementación |
| Implementación | Pieza implementada cumpliendo el contrato, en la ruta definida |
| Integración | Piezas conectadas; el punto de entrada o registro refleja el cambio |
| Superficie | Superficie operativa y conectada a la lógica que expone |
| Tests | Suite creada y pasando con el comando real del proyecto |

La definition of done siempre referencia rutas y comandos **reales del repositorio**, nunca convenciones de un framework que el repo no usa.

---

## Orden canónico detallado (por dependencias)

```text
1. Scaffold / preparación estructural (si aplica)
2. Contratos y modelos (lo que otras piezas consumen)
3. Implementaciones de los contratos
4. Infraestructura transversal que las implementaciones requieren
5. Integración / wiring entre piezas
6. Superficies (UI, CLI, API pública, docs de uso)
7. Tests de cada bloque (acompañando al bloque que validan)
```

Regla: nada se implementa antes que el contrato que lo define; nada se integra antes de existir; ninguna superficie antes que la lógica que expone.
