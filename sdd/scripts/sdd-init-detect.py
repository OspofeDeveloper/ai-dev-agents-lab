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

Exit codes:
    0 = OK (detect siempre; verify si todos los checks pasan)
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

    profiles_ok = isinstance(obj, dict) and isinstance(obj.get("profiles"), list) and "profile" not in obj
    checks.append(_check("profiles", profiles_ok,
                         "OK" if profiles_ok else 'usar el array "profiles" (acumulado) y eliminar la clave legacy "profile" (Paso 8)'))

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

    try:
        ns = parser.parse_args(argv)
    except SystemExit:
        return 1

    if ns.mode is None:
        parser.print_help(sys.stderr)
        return 1

    root = Path(ns.root).resolve() if ns.root else Path.cwd()

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

    return fail(f"modo desconocido: {ns.mode}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
