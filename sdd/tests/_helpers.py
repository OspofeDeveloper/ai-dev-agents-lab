"""Helpers compartidos por la suite de tests de sdd/scripts/ (stdlib pura).

Estrategia principal: black-box por subproceso. Cada test invoca
`python3 sdd/scripts/<x>.py <args>` sobre fixtures creados en directorios
temporales y hace assert sobre exit code + stdout/stderr + ficheros resultantes.
Esto refleja el contrato real (los scripts son CLIs) y evita el problema de
importar modulos con guion en el nombre.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Raiz del repo SDD: tests/ -> sdd/
SDD_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = SDD_ROOT / "scripts"


def run_script(script_name, *args, stdin=None, cwd=None):
    """Ejecuta scripts/<script_name> como subproceso. Devuelve CompletedProcess.

    - script_name: nombre del fichero en sdd/scripts/ (p. ej. 'sdd-seal.py').
    - args: argumentos posicionales (se convierten a str).
    - stdin: texto a pasar por stdin (o None).
    - cwd: directorio de trabajo (por defecto, la raiz del repo).
    """
    script = SCRIPTS / script_name
    cmd = [sys.executable, str(script)] + [str(a) for a in args]
    return subprocess.run(
        cmd,
        input=stdin,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else str(SDD_ROOT),
    )


def run_script_at(script_path, *args, stdin=None, cwd=None):
    """Como run_script pero con una RUTA absoluta al script (para copias en fixtures)."""
    cmd = [sys.executable, str(script_path)] + [str(a) for a in args]
    return subprocess.run(
        cmd,
        input=stdin,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


def write(path, content):
    """Escribe content en path (creando dirs intermedios). Devuelve Path."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p
