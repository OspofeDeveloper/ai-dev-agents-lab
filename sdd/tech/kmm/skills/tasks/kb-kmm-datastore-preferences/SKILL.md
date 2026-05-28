---
name: kb-kmm-datastore-preferences
description: "Base de conocimiento para usar Preferences DataStore en proyectos KMM: factory compartida, resolución de path por plataforma, ownership de keys y adapters sobre storage local."
argument-hint: "[sin argumentos]"
effort: medium
allowed-tools: [Read]
user-invocable: false
---

# kb-kmm-datastore-preferences

## Regla 1: Preferences DataStore es infraestructura local, no contrato de dominio

`Preferences DataStore` es un mecanismo técnico de persistencia clave-valor. No define por sí mismo reglas de negocio ni contratos de dominio.

Su responsabilidad es:

- persistir valores simples
- exponer lectura reactiva mediante `Flow`
- encapsular detalles locales de almacenamiento

No debe convertirse en:

- contrato de dominio expuesto directamente a toda la app
- sustituto de un repositorio o store con semántica propia
- lugar donde se mezclan reglas de auth, networking o UI

---

## Regla 2: La factory compartida vive en `commonMain`

La creación base de `Preferences DataStore` debe concentrarse en una pieza común reutilizable, normalmente basada en `PreferenceDataStoreFactory.createWithPath`.

Esa pieza compartida:

- conoce cómo crear el `DataStore<Preferences>`
- no decide paths concretos de plataforma
- no contiene dependencias de Android o iOS

→ Templates: `references/preferences_datastore_templates.md`

---

## Regla 3: El path físico se resuelve por plataforma

La ubicación real del fichero pertenece al host.

La convención correcta es:

- `commonMain` define la factory común
- `androidMain` resuelve el path con `Context`
- `iosMain` resuelve el path con APIs nativas de filesystem

La skill de DataStore no debe absorber reglas generales de platform split; solo aplica este criterio a su propio mecanismo.

→ Templates: `references/preferences_datastore_templates.md`

---

## Regla 4: El `DataStore<Preferences>` se registra como dependencia técnica

El `DataStore<Preferences>` debe registrarse en la DI como una dependencia de infraestructura.

Su registro:

- puede vivir en `nativeModule` o equivalente si la creación depende de plataforma
- no reemplaza al repositorio o adapter que expone operaciones con significado
- no convierte la DI en SSoT de ownership

La ubicación arquitectónica y el wiring se apoyan en:

- `kb-kmm-core-layer`
- `kb-kmm-feature-clean-architecture`
- `kb-koin`

---

## Regla 5: Las keys no deben mezclarse con contratos de dominio sin necesidad

Las `Preferences.Key<*>` son detalle técnico de persistencia.

La convención preferida es:

- definirlas cerca del adapter o del módulo de storage que las usa
- agruparlas por ámbito funcional o de storage
- evitar meterlas en interfaces de dominio si no aportan nada fuera de la implementación

No usar una interfaz de repositorio como simple contenedor de keys.

→ Templates: `references/preferences_datastore_templates.md`

---

## Regla 6: Sobre DataStore debe existir un adapter, store o repositorio con semántica explícita

La app no debería propagar el `DataStore<Preferences>` crudo por todas las capas.

Encima de él debe existir una pieza con intención clara, por ejemplo:

- `SessionLocalDataSource`
- `SettingsStore`
- `UserPreferencesRepository`

Esa pieza:

- traduce keys a operaciones con significado
- concentra lecturas y escrituras
- decide si expone `Flow`, `suspend fun` o ambos

---

## Regla 7: Algo debe vivir en `core` solo si varias features lo comparten

La integración de DataStore debe subir a `core` si:

- persiste estado compartido por varias features
- implementa infraestructura local transversal
- la usan auth, app o varias features distintas

Debe quedarse en una feature si:

- solo persiste estado propio de esa feature
- sus keys y operaciones no tienen significado fuera de ella

Esta skill fija el criterio para storage local. La decisión final de ownership se apoya en las skills de capa.

---

## Regla 8: DataStore no debe mezclar storage local con coordinación remota

Una misma implementación no debería combinar sin necesidad:

- lectura/escritura local en DataStore
- llamadas HTTP
- refresh de sesión
- lógica de negocio

Si un repositorio necesita ambas cosas, separar el adapter local de la coordinación superior siempre que la complejidad lo justifique.

Esta skill no prohíbe toda composición, pero fija la dirección preferida: storage local separado de integración remota.

---

## Regla 9: Helpers y extensiones de DataStore pertenecen al dominio local, no a networking

Las extensiones como guardar/leer `String`, `Boolean` o `Long` son utilidades de storage local.

Deben vivir:

- junto a DataStore
- o en un módulo local/shared de persistencia

No deben quedar ubicadas bajo paquetes de red o auth si no son realmente parte de esa responsabilidad.

---

## Regla 10: Esta skill define Preferences DataStore; no cubre Proto DataStore

Esta skill está limitada a `DataStore<Preferences>`.

No define:

- Proto DataStore
- serializers protobuf
- migraciones de esquema tipado

Si el ecosistema necesita esas decisiones, deben vivir en otra skill separada.

---

## Regla 11: Esta skill se combina con capas, DI y consumers concretos

Esta skill se combina con:

- `kb-kmm-core-layer` para decidir si el storage es transversal
- `kb-kmm-feature-clean-architecture` para storage propio de feature
- `kb-koin` para el wiring y registro
- `kb-kmm-auth-contracts` o skills de feature cuando auth o settings consumen este mecanismo

No duplicar aquí reglas de auth, app state o networking. Esta skill solo define cómo introducir Preferences DataStore con una frontera limpia.
