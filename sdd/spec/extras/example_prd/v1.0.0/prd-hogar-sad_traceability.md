# Trazabilidad de Requisitos: Aplicaciones Móviles CUIDEO - Hogar & SAD
> Generado por: wf-spec-finalize | Fecha: 2026-04-02
> Spec origen: prd-hogar-sad_spec.md

---

## Tabla RF → HU → Feature

| RF | Título RF | HU | Título HU | Feature | Estado |
|----|-----------|-----|-----------|---------|--------|
| RF-001 | Autenticación y Onboarding | HU-001 | Ver la pantalla de splash al abrir la app | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-002 | Completar el onboarding inicial | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-003 | Iniciar sesión en la app | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-004 | Activar mi cuenta (SAD) | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-005 | Registrarme en la app (Hogar) | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-029 | Cerrar sesión | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-032 | Ver pantalla de acceso revocado (SAD) | authentication | activo |
| RF-001 | Autenticación y Onboarding | HU-035 | Recuperar el acceso a mi cuenta | authentication | activo |
| RF-002 | Panel Principal | HU-006 | Navegar por el panel principal (perfil SAD) | home-dashboard | activo |
| RF-002 | Panel Principal | HU-007 | Navegar por el panel principal (perfil Hogar) | home-dashboard | activo |
| RF-002 | Panel Principal | HU-008 | Leer comunicados del tablón de anuncios | home-dashboard | activo |
| RF-002 | Panel Principal | HU-009 | Ver mensajes del sistema | home-dashboard | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-010 | Ver el detalle de un servicio (SAD) | services-management | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-011 | Consultar mis servicios asignados (SAD) | services-management | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-012 | Responder a un llamamiento (SAD) | services-management | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-013 | Gestionar notas de un servicio (SAD) | services-management | activo |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-014 | Recibir y confirmar un nuevo servicio asignado (SAD — contrato indefinido) | services-management | activo |
| RF-004 | Control Horario (Seguimiento de Tiempo) | HU-018 | Fichar entrada y salida en un servicio (SAD) | time-tracking | activo |
| RF-004 | Control Horario (Seguimiento de Tiempo) | HU-033 | Consultar historial de fichajes (SAD) | time-tracking | activo |
| RF-005 | Incidencias | HU-021 | Reportar una incidencia (SAD) | incidents | activo |
| RF-005 | Incidencias | HU-034 | Consultar historial de incidencias (SAD) | incidents | activo |
| RF-006 | Ofertas (Ofertas de Trabajo) | HU-015 | Navegar y filtrar ofertas de trabajo (Hogar) | job-offers | activo |
| RF-006 | Ofertas (Ofertas de Trabajo) | HU-016 | Solicitar una oferta de trabajo (Hogar) | job-offers | activo |
| RF-006 | Ofertas (Ofertas de Trabajo) | HU-017 | Consultar mis solicitudes de oferta (Hogar) | job-offers | activo |
| RF-007 | Mi Disponibilidad (Gestión de Disponibilidad) | HU-026 | Gestionar mi disponibilidad semanal | availability | activo |
| RF-008 | Mis Ausencias (Gestión de Ausencias) | HU-019 | Consultar historial de ausencias y saldo de vacaciones (SAD) | absences | activo |
| RF-008 | Mis Ausencias (Gestión de Ausencias) | HU-020 | Solicitar una ausencia (SAD) | absences | activo |
| RF-009 | Perfil (Gestión de Perfil) | HU-022 | Ver y editar mi perfil | profile | activo |
| RF-009 | Perfil (Gestión de Perfil) | HU-023 | Gestionar mi foto de perfil | profile | activo |
| RF-009 | Perfil (Gestión de Perfil) | HU-024 | Gestionar mis documentos (subir y firmar) | profile | activo |
| RF-009 | Perfil (Gestión de Perfil) | HU-025 | Ver el estado de mi contrato (SAD) | profile | activo |
| RF-010 | Comunicación | HU-027 | Comunicarme con coordinación mediante chat | communication | activo |
| RF-010 | Comunicación | HU-028 | Ver mi historial de conversaciones | communication | activo |
| RF-011 | Notificaciones (Notificaciones Push) | HU-030 | Recibir notificaciones push | notifications | activo |
| RF-011 | Notificaciones (Notificaciones Push) | HU-031 | Consultar el historial de notificaciones | notifications | activo |

> Los IDs de RF son inferidos de las secciones funcionales del PRD — el documento original los numera como RF-1 a RF-12 pero el RF-12 (Publicación de la Aplicación) es de alcance técnico/operativo y no genera HUs funcionales en el Spec. RF-3.4 (Historial de Servicios) se incluyó parcialmente en el alcance de HU-011 y HU-012; el historial completo de servicios completados (RF-3.5 del PRD) quedó fuera de alcance según la sección "Fuera de Alcance" del Spec.

---

## Cobertura por RF

| RF | Título RF | HUs asignadas | Features involucradas |
|----|-----------|---------------|-----------------------|
| RF-001 | Autenticación y Onboarding | HU-001, HU-002, HU-003, HU-004, HU-005, HU-029, HU-032, HU-035 | authentication |
| RF-002 | Panel Principal | HU-006, HU-007, HU-008, HU-009 | home-dashboard |
| RF-003 | Mis Servicios (Gestión de Servicios) | HU-010, HU-011, HU-012, HU-013, HU-014 | services-management |
| RF-004 | Control Horario (Seguimiento de Tiempo) | HU-018, HU-033 | time-tracking |
| RF-005 | Incidencias | HU-021, HU-034 | incidents |
| RF-006 | Ofertas (Ofertas de Trabajo) | HU-015, HU-016, HU-017 | job-offers |
| RF-007 | Mi Disponibilidad (Gestión de Disponibilidad) | HU-026 | availability |
| RF-008 | Mis Ausencias (Gestión de Ausencias) | HU-019, HU-020 | absences |
| RF-009 | Perfil (Gestión de Perfil) | HU-022, HU-023, HU-024, HU-025 | profile |
| RF-010 | Comunicación | HU-027, HU-028 | communication |
| RF-011 | Notificaciones (Notificaciones Push) | HU-030, HU-031 | notifications |

> La columna "Features involucradas" se completa tras ejecutar `/wf-spec-decompose`.

---

## Historial de cambios

| Versión | Fecha | Tipo | Descripción |
|---------|-------|------|-------------|
| 1.0 | 2026-04-02 | inicial | Generado desde spec monolítico prd-hogar-sad_spec.md |
| 1.1 | 2026-04-02 | decompose | Features asignadas desde wf-spec-decompose |
