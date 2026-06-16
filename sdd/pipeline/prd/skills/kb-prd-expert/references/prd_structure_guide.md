# Guía de Estructura del PRD para SDD

Estructura recomendada y ejemplos de cada sección de un PRD válido para el pipeline SDD.

El pipeline acepta varias organizaciones internas del alcance. Este documento muestra primero la forma preferida por actor y luego variantes válidas por RFs o por secciones funcionales.

---

## Estructura completa

```markdown
---
type: product-requirements
product: [nombre del producto]
version: 1.0
created: [YYYY-MM-DD]
status: draft | in-review | approved
---

# PRD: [Nombre del Producto]
> **Aprobado por:** [pendiente de review — lo escribe wf-prd-review cuando el veredicto es LISTO; ver kb-traceability-rules Regla 10]

## Resumen Ejecutivo

### Visión del Producto
[Una o dos frases que describen el problema que resuelve y para quién]

### Objetivos de Negocio
- [Objetivo 1 — qué valor aporta al negocio o al usuario]
- [Objetivo 2]
- [Objetivo 3]

### Puntos Clave
- [Característica diferencial 1 del producto]
- [Característica diferencial 2]

---

## Actores

| Actor | Descripción | Capacidades en este producto |
|-------|-------------|------------------------------|
| [Nombre] | [Rol en el negocio] | [Resumen de lo que puede hacer] |
| [Nombre] | [Rol en el negocio] | [Resumen de lo que puede hacer] |

---

## Alcance

### Dentro del Alcance

#### Funcionalidades comunes (todos los actores)
- [Capacidad disponible para cualquier actor]
- [Capacidad disponible para cualquier actor]

#### Solo [Actor A]
- [Capacidad exclusiva de este actor]
- [Capacidad exclusiva de este actor]

#### Solo [Actor B]
- [Capacidad exclusiva de este actor]

---

### Fuera del Alcance

- [Funcionalidad excluida]: [motivo — fase futura / otro sistema / fuera del MVP]
- [Funcionalidad excluida]: [motivo]

---

## Reglas de Negocio Transversales

- [Restricción o comportamiento que afecta a múltiples features]
- [Restricción o comportamiento que afecta a múltiples features]
```

---

## Ejemplo de Resumen Ejecutivo correcto

```markdown
### Visión del Producto
Empoderar a las trabajadoras de cuidado con una app móvil que simplifique su jornada diaria:
gestión de servicios, registro de tiempo y comunicación con su coordinador, todo desde el móvil.

### Objetivos de Negocio
- Reducir la carga administrativa de las trabajadoras eliminando el papeleo
- Garantizar el cumplimiento de los servicios con validación de presencia
- Mejorar la comunicación entre trabajadoras y coordinadores

### Puntos Clave
- Dos perfiles de usuario (Hogar y SAD) con funcionalidades diferenciadas
- Registro de tiempo validado por ubicación para garantizar el cumplimiento
```

---

## Ejemplo de sección Actores correcta

```markdown
## Actores

| Actor | Descripción | Capacidades en este producto |
|-------|-------------|------------------------------|
| Trabajadora Hogar | Empleada de hogar que gestiona servicios domésticos | Ver ofertas, solicitar trabajos, gestionar su perfil y disponibilidad |
| Trabajadora SAD | Auxiliar de ayuda a domicilio con servicios asignados | Ver servicios asignados, fichar entrada/salida, reportar incidencias |
```

---

## Ejemplo de fuera-de-alcance correcto

```markdown
### Fuera del Alcance
- Gestión de nóminas y pagos: responsabilidad del back-office, sin interfaz en la app
- Videollamadas con coordinadores: fase futura, no incluida en el MVP
- Administración de usuarios y roles: gestionada exclusivamente desde el panel de back-office
- Histórico de servicios anteriores a la migración: los datos pre-migración no son accesibles desde la app
```

---

## Ejemplo de reglas de negocio transversales correctas

```markdown
## Reglas de Negocio Transversales
- Los documentos adjuntos deben ser imágenes (JPG, PNG) o documentos (PDF, DOC, DOCX) con un máximo de 10 MB
- La sesión de usuario se mantiene activa. Solo se solicita login de nuevo si el usuario cierra sesión explícitamente
- Solo las trabajadoras con contrato activo pueden acceder a las funcionalidades de servicios
```

---

## Señales de un PRD bien escrito

- Cada ítem del alcance tiene un actor explícito como sujeto
- El fuera-de-alcance nombra funcionalidades concretas, no genéricas
- No aparece ningún término tecnológico (frameworks, protocolos, arquitectura)
- Un cliente de negocio no técnico puede leerlo y validarlo sin ayuda
- Las reglas de negocio describen restricciones funcionales, no restricciones técnicas

---

## Variante válida: PRD organizado por RFs

```markdown
## Actores

| Actor | Descripción | Capacidades en este producto |
|-------|-------------|------------------------------|
| Cuidadora | Profesional de campo | Gestionar servicios, registrar jornada, comunicar incidencias |
| Coordinador | Responsable operativo | Revisar disponibilidad, gestionar asignaciones |

## Alcance

### RF-001 Autenticación y sesión
- La trabajadora puede autenticarse con sus credenciales corporativas
- La trabajadora puede mantener su sesión activa entre usos normales de la app

### RF-002 Gestión de servicios
- La cuidadora puede consultar sus servicios asignados
- La cuidadora puede ver el detalle operativo de cada servicio

### Fuera del Alcance
- Gestión de nómina: fuera de esta versión
```

**Condición:** aunque el alcance se estructure por RFs, los actores deben declararse explícitamente.

---

## Variante válida: PRD organizado por secciones funcionales

```markdown
## Actores

| Actor | Descripción | Capacidades en este producto |
|-------|-------------|------------------------------|
| Trabajadora | Ejecuta el servicio | Consultar agenda, fichar, reportar incidencias |

## Alcance

### Autenticación
- La trabajadora puede iniciar sesión
- La trabajadora puede cerrar sesión

### Control horario
- La trabajadora puede registrar entrada y salida
- La trabajadora puede consultar el estado de su jornada

### Incidencias
- La trabajadora puede reportar una incidencia asociada a un servicio

### Fuera del Alcance
- Gestión offline completa: fase futura
```

**Condición:** las secciones funcionales no deben ocultar qué actor realiza cada capacidad.
