# `docs/` — Sitio de documentación (MkDocs)

**Qué es.** La documentación **de cara al usuario** del ecosistema, publicada como sitio MkDocs
Material. Es la capa narrativa y didáctica; no es documentación interna de arquitectura.

**Qué contiene.**

```
docs/
├── index.md          portada del sitio
├── empezar/          onboarding (tu primera feature)
├── guias/            por perfil: desarrollador, producto, diseñador, contribuidor
├── entender/         visión funcional y diseño técnico (con diagramas)
├── referencia/       catálogo de skills, scripts, glosario
├── requirements.txt  dependencias de build (mkdocs material, etc.)
└── ROADMAP.md        roadmap interno (NO publicado — ver exclude_docs)
```

La config está en `../mkdocs.yml`. El **CI** (`.github/workflows/docs.yml`) hace
`mkdocs gh-deploy` a la rama `gh-pages` al hacer push a `main`. El output local (`../site/`) es
regenerable y está en `.gitignore`. `exclude_docs` de `mkdocs.yml` deja fuera del sitio los
documentos internos (`ROADMAP.md`, `audit_*.md`).

**Qué NO es / qué no va aquí.**
- No es el mapa en-repo para quien navega el código: eso son `../README.md` y los `DIAGRAMS.md`.
- No es el contrato de comportamiento del ecosistema: eso es `../conformance/` (Casos de Uso).
- No es SSoT de reglas: las reglas viven en las `kb-*`; aquí se explican para humanos.

**A quién sirve.** A los **usuarios** del ecosistema (devs, PMs, diseñadores, contribuidores) que
leen el sitio publicado. Los `README.md` por directorio de este repo (incluido este) **no** entran
al sitio: solo se publica lo que cuelga de `docs/`.
