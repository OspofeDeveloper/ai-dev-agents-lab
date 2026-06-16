# Plantilla de reporte de auditoría de accesibilidad

```
=== A11Y AUDIT REPORT ===
Path: <design_path>
Views: <views_path o N/A>
Target: <AA|AAA>
Fecha: <ISO>

== Contraste ==
[CRITICO] light: on-surface-muted/surface = 3.2:1 (requerido 4.5:1)
[CRITICO] dark:  on-warning/warning = 2.8:1 (requerido 4.5:1)

== Touch targets ==
[ALTO] chip-removable: 32x32 (minimo 44pt)

== Motion ==
OK

== Declaraciones ==
[MEDIO] Falta documentar politica de dynamic type en seccion Accessibility

== Vistas (si aplica) ==
[ALTO] login_views.md > Vista 'login': focus order no declarado en modal

== Total ==
2 criticos, 2 altos, 1 medio.
Estado: FAIL
```
