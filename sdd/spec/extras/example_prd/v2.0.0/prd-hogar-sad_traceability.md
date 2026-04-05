# Trazabilidad de Requisitos: CUIDEO - Hogar & SAD
> Generado por: wf-spec-express | Fecha: 2026-04-03
> PRD origen: prd-hogar-sad.md

---

## Tabla RF -> HU -> Feature

| RF | Titulo RF | HU | Titulo HU | Feature | Estado |
|----|-----------|-----|-----------|---------|--------|
| RF-1 | Autenticacion y Onboarding | HU-001 | Splash de bienvenida | autenticacion-onboarding | activo |
| RF-1 | Autenticacion y Onboarding | HU-002 | Onboarding de la app | autenticacion-onboarding | activo |
| RF-1 | Autenticacion y Onboarding | HU-003 | Registro en la app (Hogar) | autenticacion-onboarding | activo |
| RF-1 | Autenticacion y Onboarding | HU-004 | Activacion de cuenta (SAD) | autenticacion-onboarding | activo |
| RF-1 | Autenticacion y Onboarding | HU-005 | Inicio de sesion | autenticacion-onboarding | activo |
| RF-1 | Autenticacion y Onboarding | HU-006 | Recuperacion de acceso | autenticacion-onboarding | activo |
| RF-1 | Autenticacion y Onboarding | HU-007 | Gestion del token de sesion | autenticacion-onboarding | activo |
| RF-1 | Autenticacion y Onboarding | HU-008 | Cierre de sesion | autenticacion-onboarding | activo |
| RF-1 | Autenticacion y Onboarding | HU-009 | Pantalla de acceso revocado (SAD) | autenticacion-onboarding | activo |
| RF-2 | Panel Principal | HU-001 | Accesos directos del panel | panel-principal | activo |
| RF-2 | Panel Principal | HU-002 | Tablon de anuncios | panel-principal | activo |
| RF-2 | Panel Principal | HU-003 | Mensajes del sistema | panel-principal | activo |
| RF-3 | Mis Servicios | HU-001 | Listado de servicios | gestion-servicios | activo |
| RF-3 | Mis Servicios | HU-002 | Detalle de servicio | gestion-servicios | activo |
| RF-3 | Mis Servicios | HU-003 | Notas de servicio | gestion-servicios | activo |
| RF-3 | Mis Servicios | HU-004 | Respuesta a llamamientos | gestion-servicios | activo |
| RF-3 | Mis Servicios | HU-005 | Historial de servicios | gestion-servicios | activo |
| RF-3 | Mis Servicios | HU-006 | Nuevo servicio asignado (indefinidos) | gestion-servicios | activo |
| RF-4 | Control Horario | HU-001 | Fichar entrada y salida | control-horario | activo |
| RF-4 | Control Horario | HU-002 | Consultar historial de fichaje | control-horario | activo |
| RF-5 | Incidencias | HU-001 | Reportar incidencia | incidencias | activo |
| RF-5 | Incidencias | HU-002 | Consultar historial de incidencias | incidencias | activo |
| RF-6 | Ofertas | HU-001 | Navegar ofertas disponibles | ofertas-trabajo | activo |
| RF-6 | Ofertas | HU-002 | Solicitar oferta | ofertas-trabajo | activo |
| RF-6 | Ofertas | HU-003 | Consultar mis solicitudes | ofertas-trabajo | activo |
| RF-7 | Mi Disponibilidad | HU-001 | Gestionar calendario de disponibilidad | disponibilidad | activo |
| RF-8 | Mis Ausencias | HU-001 | Solicitar ausencia | ausencias | activo |
| RF-8 | Mis Ausencias | HU-002 | Consultar historial y saldo | ausencias | activo |
| RF-9 | Perfil | HU-001 | Ver y editar perfil | perfil | activo |
| RF-9 | Perfil | HU-002 | Gestionar foto de perfil | perfil | activo |
| RF-9 | Perfil | HU-003 | Gestionar documentos | perfil | activo |
| RF-9 | Perfil | HU-004 | Capturar firma digital | perfil | activo |
| RF-9 | Perfil | HU-005 | Ver estado del contrato (SAD) | perfil | activo |
| RF-9 | Perfil | HU-006 | Completar perfil para aplicar (Hogar) | perfil | activo |
| RF-10 | Comunicacion | HU-001 | Iniciar conversacion | comunicacion | activo |
| RF-10 | Comunicacion | HU-002 | Consultar conversaciones | comunicacion | activo |
| RF-10 | Comunicacion | HU-003 | Enviar y recibir mensajes | comunicacion | activo |
| RF-11 | Notificaciones | HU-001 | Recibir notificaciones push | notificaciones | activo |
| RF-11 | Notificaciones | HU-002 | Recibir recordatorios automaticos | notificaciones | activo |

<!--
  RF-12 (Publicacion de la Aplicacion) no genera HUs funcionales para la trabajadora.
  Se trata de requisitos de publicacion y branding que pertenecen al Plan tecnico, no al Spec funcional.
-->

---

## Cobertura por RF

| RF | Titulo RF | HUs asignadas | Features involucradas |
|----|-----------|---------------|-----------------------|
| RF-1 | Autenticacion y Onboarding | HU-001 a HU-009 | autenticacion-onboarding |
| RF-2 | Panel Principal | HU-001 a HU-003 | panel-principal |
| RF-3 | Mis Servicios | HU-001 a HU-006 | gestion-servicios |
| RF-4 | Control Horario | HU-001 a HU-002 | control-horario |
| RF-5 | Incidencias | HU-001 a HU-002 | incidencias |
| RF-6 | Ofertas | HU-001 a HU-003 | ofertas-trabajo |
| RF-7 | Mi Disponibilidad | HU-001 | disponibilidad |
| RF-8 | Mis Ausencias | HU-001 a HU-002 | ausencias |
| RF-9 | Perfil | HU-001 a HU-006 | perfil |
| RF-10 | Comunicacion | HU-001 a HU-003 | comunicacion |
| RF-11 | Notificaciones | HU-001 a HU-002 | notificaciones |

---

## Historial de cambios

| Version | Fecha | Tipo | Descripcion |
|---------|-------|------|-------------|
| 1.0 | 2026-04-03 | express | Generado via wf-spec-express |
