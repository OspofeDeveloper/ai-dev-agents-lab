#!/usr/bin/env python3
"""Detección/verificación determinista para wf-project-init (Fase: hardening init).

`wf-project-init` recitaba en prosa+bash la lógica determinista de su onboarding:
find-up del raíz del proyecto en monorepos, detección de estado previo, carpetas
candidatas de artefactos, detección de stack, y la verificación post-install. Eso
es exactamente lo que el ecosistema convierte en scripts (recolección determinista,
no agente): retecleado por el modelo cada init, no testeable. Este script lo hace
ÚNICO y testeable.

Herramienta de ECOSISTEMA, no de proyecto: NO se distribuye a `.sdd/scripts/`. Se
invoca vía `$SDD_HOME/scripts/sdd-init-detect.py` — disponible pre-install igual que
`$SDD_HOME/install.sh` (el init corre antes de que `.sdd/scripts/` exista). Mismo
patrón que `sdd-structural-lint.py` / `sdd-scaffold.py`.

Subcomandos:
    detect [--root <dir>]
        Emite (JSON) el estado que el Paso 5 del skill consume como `KNOWN_STATE`:
        find-up de un init/modo previo (techo en el git toplevel), estado previo,
        carpetas candidatas de artefactos y stack/tipo detectados. Pre-install:
        no requiere `.sdd/scripts/`.

    verify --phases <f1,f2,...> [--root <dir>]
        Checks deterministas post-install (Paso 9). Emite (JSON) un check por línea
        del checklist. Exit 2 si ALGÚN check falla (gate bloqueante CU-1.k), 0 si
        todos pasan. Acepta el esquema standalone (`artifacts`) y consumer
        (`artifacts_source`).

    repair-plan [--root <dir>]
        Plan determinista de reparación de un `init-incomplete` (extend, Paso 3b/5).
        Lee `project-init.json` y calcula, sin intervención del agente: qué fases
        están declaradas pero no instaladas (`missing_phases`) y el `design_role`
        canónico derivado de la topología (`expected_design_role`). El agente APLICA
        el plan — no re-decide ni pregunta el rol (la reparación instala lo declarado;
        quitar una fase es un cambio de alcance explícito, no reparación). Pre-install
        no aplica: requiere un `project-init.json` previo.

    target-platforms --targets <t1,t2,...>
        Valida una lista de design targets contra su convención (familia obligatoria
        de {mobile,web,desktop}) y deriva las familias `target_platforms` (D-011,
        foundational). Emite (JSON) `valid`/`invalid`/`target_platforms`/`all_valid`.
        Función pura testeada lista para el wiring de la topología `design` (diferido);
        hoy no tiene aún consumidor — mismo patrón pre-wiring que tuvo `repair-plan`.

Exit codes:
    0 = OK (detect/repair-plan siempre; verify si todos los checks pasan)
    1 = error de uso (argumentos inválidos)
    2 = (verify) al menos un check FALLÓ
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# --- Detección de stack (Paso 4 del SKILL). Orden = precedencia. ---
PHASES = ["prd", "spec", "design", "plan", "tasks"]

ENFORCEMENT_SCRIPTS = [
    "sdd-gate-check.py", "sdd-seal.py", "sdd-task-state.py",
    "sdd-sync-check.py", "sdd-skill-allow.py",
]

# Carpetas candidatas por fase (Paso 3d).
ARTIFACT_CANDIDATE_DIRS = {
    "spec": ["specs", "docs/specs", "documentation/specs"],
    "prd": ["docs/prd", "product", "docs/product", "requirements"],
    "design": ["docs/design", "design-system"],
}

# Rol de design derivado de la topología (SSoT en código del Paso 5 del SKILL:
# authoring L29/229 → system, consumer L252 → feature, standalone L274 → full).
# El rol NO depende de has_ui: en consumer, has_ui decide si design ESTÁ presente,
# no su rol. Si design no está declarado, no hay rol (null).
DESIGN_ROLE_BY_TOPOLOGY = {
    "authoring": "system",
    "consumer": "feature",
    "standalone": "full",
}

# --- Design targets y derivación de target_platforms (D-011, foundational). ---
# Familias de plataforma canónicas: token OBLIGATORIO (primer segmento) de un
# design target. Es el vocabulario que consumen a11y (mobile/web/desktop),
# `target_tool` (stitch|web-generic) y layout. `tablet` NO es familia: es un
# form-factor dentro de `mobile`/`desktop` (otro token del target, p. ej.
# `mobile-tablet`). SSoT del vocabulario de familias del ecosistema (D-011 dec. B).
DESIGN_TARGET_FAMILIES = ("mobile", "web", "desktop")

# Convención de etiqueta de design target: `<familia>[-<plataforma>][-<formfactor>]`.
# Tokens kebab-case alfanuméricos en minúscula; la familia se valida aparte.
_DESIGN_TARGET_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(msg: str) -> int:
    sys.stderr.write(f"ERROR: {msg}\n")
    return 1


def _has(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def _contains(root: Path, rel: str, needle: str, *, ci: bool = False) -> bool:
    """¿El fichero <rel> existe y contiene <needle>? (equivalente a `grep -q`)."""
    p = root / rel
    if not p.is_file():
        return False
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return (needle.lower() in text.lower()) if ci else (needle in text)


def git_toplevel(start: Path) -> Path | None:
    try:
        r = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip()).resolve()
    except (OSError, ValueError):
        pass
    return None


def find_up_sdd_root(start: Path) -> tuple[Path | None, Path]:
    """Busca hacia arriba un init/modo previo, con techo en el git toplevel.

    Espejo de la lógica del hook de sesión y del Paso 3.0 del SKILL: fuera de git
    el techo es el propio `start` (solo se mira el cwd). Devuelve (sdd_root|None,
    ceiling).
    """
    ceiling = git_toplevel(start) or start
    d = start
    while True:
        if (d / ".sdd/project-init.json").is_file() or (d / ".claude/sdd-mode.json").is_file():
            return d, ceiling
        if d == ceiling or d == d.parent:
            return None, ceiling
        d = d.parent


def detect_stack(root: Path) -> tuple[str | None, str | None, str | None]:
    """(detected_stack, detected_type, app_framework) según el Paso 4 del SKILL."""
    gradle = _has(root, "gradle/libs.versions.toml")
    ios_app = _has(root, "iosApp")
    compose_app = _has(root, "composeApp")
    flutter = _contains(root, "pubspec.yaml", "flutter:")
    android_build = _has(root, "app/build.gradle.kts")
    next_js = _contains(root, "package.json", '"next"')
    vite_react = _contains(root, "package.json", '"vite"') and _contains(root, "package.json", '"react"')
    astro = _has(root, "astro.config.mjs") or _has(root, "astro.config.ts")
    ktor = _contains(root, "build.gradle.kts", "ktor")
    express = _contains(root, "package.json", '"express"')
    fastapi = _contains(root, "pyproject.toml", "fastapi") or _contains(root, "requirements.txt", "fastapi", ci=True)

    if gradle and (ios_app or compose_app):
        return "kmm", "app", "compose_multiplatform"
    if flutter:
        return "flutter", "app", "flutter"
    if android_build and not ios_app:
        return "android", "app", "android"
    if next_js:
        return "next", "web", None
    if vite_react:
        return "vite-react", "web", None
    if astro:
        return "astro", "web", None
    if ktor:
        return "ktor", "backend", None
    if express:
        return "node-express", "backend", None
    if fastapi:
        return "fastapi", "backend", None
    return None, None, None


def read_mode(root: Path) -> str | None:
    p = root / ".claude/sdd-mode.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("mode")
    except (OSError, ValueError):
        return None


def detect(root: Path) -> dict:
    sdd_root, ceiling = find_up_sdd_root(root)
    installed = [
        f for f in PHASES
        if (root / f".claude/rules/sdd-{f}.md").is_file()
        or (root / f / ".claude/CLAUDE.md").is_file()
    ]
    candidates = {
        phase: [d for d in dirs if (root / d).is_dir()]
        for phase, dirs in ARTIFACT_CANDIDATE_DIRS.items()
    }
    candidates = {k: v for k, v in candidates.items() if v}
    stack, ptype, framework = detect_stack(root)
    return {
        "cwd": str(root),
        "ceiling": str(ceiling),
        "sdd_root": str(sdd_root) if sdd_root else None,
        "sdd_root_is_ancestor": bool(sdd_root) and sdd_root != root,
        "init_found": (root / ".sdd/project-init.json").is_file(),
        "mode_found": (root / ".claude/sdd-mode.json").is_file(),
        "mode": read_mode(root),
        "installed_phases": installed,
        "artifact_candidates": candidates,
        "detected_stack": stack,
        "detected_type": ptype,
        "app_framework": framework,
    }


def _check(name: str, ok: bool, message: str) -> dict:
    return {"check": name, "ok": ok, "message": message}


def verify(root: Path, phases: list[str]) -> list[dict]:
    checks = []
    for f in phases:
        ok = (root / f".claude/rules/sdd-{f}.md").is_file()
        checks.append(_check(
            f"fase-{f}", ok,
            "OK" if ok else f"falta .claude/rules/sdd-{f}.md — ejecutar: install.sh {f}"))

    checks.append(_check("claude-md", _has(root, ".claude/CLAUDE.md"),
                         "OK" if _has(root, ".claude/CLAUDE.md") else "falta .claude/CLAUDE.md (Paso 7)"))

    init_json = root / ".sdd/project-init.json"
    checks.append(_check("init-json", init_json.is_file(),
                         "OK" if init_json.is_file() else "falta .sdd/project-init.json (Paso 8)"))

    obj = None
    if init_json.is_file():
        try:
            obj = json.loads(init_json.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            obj = None

    schema_ok = isinstance(obj, dict) and obj.get("dispatcher") == "wf-project-init"
    checks.append(_check("schema", schema_ok,
                         "OK" if schema_ok else 'reescribir con los campos exactos del Paso 8 ("dispatcher": "wf-project-init")'))

    # standalone usa "artifacts"; consumer usa "artifacts_source" (CU-1.i).
    artifacts_ok = isinstance(obj, dict) and ("artifacts" in obj or "artifacts_source" in obj)
    checks.append(_check("artifacts-map", artifacts_ok,
                         "OK" if artifacts_ok else 'falta "artifacts" (standalone) o "artifacts_source" (consumer) (Paso 8)'))

    # Esquema nuevo (topología-first): el eje primario es "topology"; las claves
    # legacy "profiles"/"profile"/"type" ya no son válidas (break limpio).
    topo_ok = (
        isinstance(obj, dict)
        and obj.get("topology") in {"authoring", "consumer", "standalone"}
        and "profiles" not in obj and "profile" not in obj and "type" not in obj
    )
    checks.append(_check("topology", topo_ok,
                         "OK" if topo_ok else 'usar "topology" (authoring|consumer|standalone) y eliminar las claves legacy "profiles"/"profile"/"type" (Paso 8)'))

    scripts_ok = all((root / ".sdd/scripts" / s).is_file() for s in ENFORCEMENT_SCRIPTS)
    checks.append(_check("enforcement-scripts", scripts_ok,
                         "OK" if scripts_ok else "copiar los scripts de enforcement desde $SDD_HOME/scripts/ (Paso 6)"))

    ver_ok = _has(root, ".sdd/sdd-version.json")
    checks.append(_check("sdd-version", ver_ok,
                         "OK" if ver_ok else "re-ejecutar install.sh para sellar la versión (Paso 6)"))

    gi = root / ".gitignore"
    gi_ok = gi.is_file() and any(
        line.strip() == ".claude/settings.local.json"
        for line in gi.read_text(encoding="utf-8", errors="replace").splitlines()
    )
    checks.append(_check("gitignore", gi_ok,
                         "OK" if gi_ok else "añadir la línea .claude/settings.local.json a .gitignore (Paso 7)"))

    return checks


def derive_design_role(topology: str | None, design_declared: bool) -> str | None:
    """`design_role` canónico dada la topología. None si design no está declarado.

    Es la función pura que el agente improvisaba en prosa al reparar un init a
    medias: dado que `phases` (el contrato) declara design, el rol queda
    determinado por la topología sin ambigüedad — no hay nada que preguntar.
    """
    if not design_declared:
        return None
    return DESIGN_ROLE_BY_TOPOLOGY.get(topology)


def parse_design_target(label: str) -> tuple[str, list[str]] | None:
    """`(familia, tokens_extra)` de un design target válido, o None si no lo es.

    Convención validada (D-011, decisión B): `<familia>[-<plataforma>][-<formfactor>]`.
    La FAMILIA (primer token) es obligatoria y debe estar en DESIGN_TARGET_FAMILIES;
    el resto de tokens son libres (kebab-case alfanumérico en minúscula). Net-new:
    no existía. Es la pieza que el agente improvisaría al validar etiquetas en prosa.
    """
    if not isinstance(label, str) or not _DESIGN_TARGET_RE.match(label):
        return None
    parts = label.split("-")
    family = parts[0]
    if family not in DESIGN_TARGET_FAMILIES:
        return None
    return family, parts[1:]


def is_valid_design_target(label: str) -> bool:
    """¿`label` respeta la convención de design target (familia válida)?"""
    return parse_design_target(label) is not None


def derive_target_platforms(design_targets: list[str]) -> list[str]:
    """Familias `target_platforms` derivadas de los design targets declarados.

    Cada target aporta su familia (primer token); el resultado son las familias
    DISTINTAS en orden canónico (mobile, web, desktop). Los targets inválidos
    (familia desconocida o patrón roto) se ignoran — validarlos es cosa de
    `is_valid_design_target`. Net-new (D-011, sección E): NO existía hoy; sigue el
    patrón de `derive_design_role` (función pura testeada, D-010). Ejemplo:
    `["mobile-android", "mobile-ios", "desktop"]` -> `["mobile", "desktop"]`.
    """
    if not isinstance(design_targets, list):
        return []
    found = set()
    for label in design_targets:
        parsed = parse_design_target(label)
        if parsed is not None:
            found.add(parsed[0])
    return [fam for fam in DESIGN_TARGET_FAMILIES if fam in found]


def design_targets_report(targets: list[str]) -> dict:
    """Reporte determinista de una lista de design targets (subcomando target-platforms).

    Valida cada etiqueta contra la convención (familia obligatoria) y deriva las
    familias `target_platforms`. Pensado para que `wf-project-init` —cuando aterrice
    la topología `design` (D-011, diferido)— compute `target_platforms` y rechace
    etiquetas inválidas sin re-decidir en prosa, igual que `repair-plan` hace con
    `design_role`. Hoy es foundational: testeado, listo para wiring.
    """
    valid = [t for t in targets if is_valid_design_target(t)]
    invalid = [t for t in targets if not is_valid_design_target(t)]
    return {
        "design_targets": list(targets),
        "valid": valid,
        "invalid": invalid,
        "target_platforms": derive_target_platforms(targets),
        "all_valid": not invalid,
    }


def repair_plan(root: Path) -> dict:
    """Plan determinista de reparación de un `init-incomplete` (extend, Paso 3b/5).

    Lee `project-init.json` y calcula qué fases declaradas faltan por instalar y el
    `design_role` canónico, para que el agente APLIQUE el plan en vez de re-decidir
    (en concreto, no preguntar el rol). `phases` es el contrato: lo declarado se
    instala; quitar una fase es un cambio de alcance, no una reparación.
    """
    init_json = root / ".sdd/project-init.json"
    obj = None
    if init_json.is_file():
        try:
            obj = json.loads(init_json.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            obj = None

    installed = [
        f for f in PHASES
        if (root / f".claude/rules/sdd-{f}.md").is_file()
        or (root / f / ".claude/CLAUDE.md").is_file()
    ]

    if not isinstance(obj, dict):
        return {
            "init_found": init_json.is_file(),
            "init_readable": False,
            "topology": None,
            "declared_phases": [],
            "installed_phases": installed,
            "missing_phases": [],
            "design_declared": False,
            "design_role_in_json": None,
            "expected_design_role": None,
            "design_role_consistent": True,
            "needs_repair": False,
        }

    topology = obj.get("topology")
    raw_phases = obj.get("phases")
    declared_set = {p for p in raw_phases if isinstance(p, str)} if isinstance(raw_phases, list) else set()
    declared = [p for p in PHASES if p in declared_set]  # orden canónico
    missing = [p for p in declared if p not in installed]

    design_declared = "design" in declared_set
    role_json = obj.get("design_role")
    expected_role = derive_design_role(topology, design_declared)
    role_consistent = role_json == expected_role

    return {
        "init_found": True,
        "init_readable": True,
        "topology": topology,
        "declared_phases": declared,
        "installed_phases": installed,
        "missing_phases": missing,
        "design_declared": design_declared,
        "design_role_in_json": role_json,
        "expected_design_role": expected_role,
        "design_role_consistent": role_consistent,
        "needs_repair": bool(missing) or not role_consistent,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="sdd-init-detect.py", add_help=True, description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode")

    p_detect = sub.add_parser("detect", help="estado del proyecto (pre-install)")
    p_detect.add_argument("--root", default=None, help="raíz a analizar (default: cwd)")
    p_detect.add_argument("--json", action="store_true", help="salida JSON (default)")

    p_verify = sub.add_parser("verify", help="checks post-install (Paso 9)")
    p_verify.add_argument("--phases", required=True, help="fases instaladas, separadas por comas")
    p_verify.add_argument("--root", default=None, help="raíz a verificar (default: cwd)")
    p_verify.add_argument("--json", action="store_true", help="salida JSON (default)")

    p_repair = sub.add_parser("repair-plan", help="plan de reparación de init-incomplete (Paso 3b/5)")
    p_repair.add_argument("--root", default=None, help="raíz a analizar (default: cwd)")
    p_repair.add_argument("--json", action="store_true", help="salida JSON (default)")

    p_targets = sub.add_parser("target-platforms", help="familias derivadas + validación de design targets (D-011)")
    p_targets.add_argument("--targets", required=True, help="design targets separados por comas")
    p_targets.add_argument("--json", action="store_true", help="salida JSON (default)")

    try:
        ns = parser.parse_args(argv)
    except SystemExit:
        return 1

    if ns.mode is None:
        parser.print_help(sys.stderr)
        return 1

    ns_root = getattr(ns, "root", None)  # target-platforms no opera sobre una raíz
    root = Path(ns_root).resolve() if ns_root else Path.cwd()

    if ns.mode == "detect":
        print(json.dumps(detect(root), indent=2, ensure_ascii=False))
        return 0

    if ns.mode == "verify":
        phases = [p.strip() for p in ns.phases.split(",") if p.strip()]
        if not phases:
            return fail("--phases vacío")
        checks = verify(root, phases)
        print(json.dumps(checks, indent=2, ensure_ascii=False))
        return 0 if all(c["ok"] for c in checks) else 2

    if ns.mode == "repair-plan":
        print(json.dumps(repair_plan(root), indent=2, ensure_ascii=False))
        return 0

    if ns.mode == "target-platforms":
        targets = [t.strip() for t in ns.targets.split(",") if t.strip()]
        print(json.dumps(design_targets_report(targets), indent=2, ensure_ascii=False))
        return 0

    return fail(f"modo desconocido: {ns.mode}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
