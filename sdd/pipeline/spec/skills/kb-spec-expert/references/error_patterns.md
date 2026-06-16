# Patrones de Error y Contaminación Técnica

Estos son los errores más frecuentes que debes detectar y corregir al revisar un Spec.

## Contaminación de Stack Técnico

- `"El sistema usará una API REST"` → Reescribe: "El sistema consulta información actualizada de X servicio externo."
- `"Implementado en Kotlin Multiplatform"` → Elimínalo. El Spec no menciona tecnologías.
- `"La base de datos guarda las preferencias como JSON"` → Elimínalo. Es arquitectura técnica.
- `"El login usa OAuth 2.0 con PKCE"` → Reescribe: "El usuario puede autenticarse con su cuenta de [servicio externo]."
- `"La pantalla usa un layout de tarjetas con Material Design"` → Simplifica: "El usuario ve una lista de ítems, cada uno con [campos de datos]."

## Ambigüedad de Navegación

- `"El usuario es dirigido al lugar apropiado"` → Enumera todos los destinos posibles y cuándo aplica cada uno.
- `"La app abre el contenido correspondiente"` → Reescribe: "La app abre [X] identificado por [contexto funcional disponible en la notificación]."
- **Datos de navegación implícitos**: Si el journey asume que el sistema sabe adónde ir sin explicar qué información porta la notificación → Spec ambiguo. Define el contexto funcional sin entrar en implementación.

## Criterios de Aceptación Defectuosos

- **Criterios de éxito vagos**: "La función funciona correctamente." → No es testeable. Debe especificar el resultado observable.
- **Solo happy path**: El Spec describe únicamente el flujo exitoso → Incompleto. Falta definir estados de error y flujos alternativos.
- **GIVEN/WHEN/THEN incompleto**: Falta la precondición (GIVEN) o el resultado verificable (THEN).

## Cómo aplicar este archivo

Antes de emitir tu veredicto de pureza, recorre esta lista y busca cada patrón en el Spec. Si encuentras una coincidencia, cítala textualmente en tu revisión y propón la reescritura correcta.
