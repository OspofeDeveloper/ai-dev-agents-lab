# Checklist de cierre de feature KMM

Verificar antes de declarar completa la arquitectura interna de una feature.

---

- [ ] La pantalla con ViewModel usa `presentation/<pantalla>/viewmodel/` como ubicación preferida
- [ ] El ViewModel expone `onIntent(intent)` como único punto de entrada
- [ ] El naming de `State`, `Intent` y `Events` sigue las convenciones de `kb-plan-kmm-navigation-viewmodel-events`
- [ ] La capa `presentation` no mezcla DTOs, data sources ni detalles de infraestructura
- [ ] Los repositorios tienen interfaz en `domain` e implementación en `data` (no colapsados)
- [ ] Nada de `data` (DTOs, status codes, HttpResponse) cruza la frontera hacia `presentation` o `domain`
- [ ] Las piezas compartidas entre features están en `core`, no como dependencias cruzadas entre features
- [ ] Los efectos del ViewModel describen hechos, no destinos de navegación concretos
