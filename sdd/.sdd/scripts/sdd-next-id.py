#!/usr/bin/env python3
# sdd-version: 0.37.0+3cdfd2d
"""Asignador determinista del siguiente ID secuencial (ROADMAP 11.2b).

Varias numeraciones se asignaban hoy por prosa ("escanea el archivo y asigna el
siguiente"): B-00X en _bugs.md, TC-XXX en _qa_plan.md, F-001 directo en
fast-track. Si el modelo cuenta mal, hay COLISION de IDs y el registro / el
indice de features se corrompe. Este script escanea los IDs ya usados del
prefijo en los archivos dados y emite el siguiente libre — pseudo-funcion pura,
mismo patron que `sdd-amend.py next-ref` (que ya hace esto para E-00X).

NO escribe: solo emite el ID por stdout. El workflow escribe la entrada con ese
ID (igual que next-ref). Asi el script no puede malformar el archivo.

Distincion de prefijos: un lookbehind evita que un prefijo sea sufijo de otro
token — `F` NO matchea `RF-001` ni `F-C-003`; `R` NO matchea `CR-001`. Las
familias `F` y `F-C` son secuencias independientes.

Uso:
    sdd-next-id.py <prefijo> <archivo> [<archivo2> ...] [--width N]

  <prefijo>   literal del ID sin el guion ni el numero: B | TC | F | F-C | TD | ...
  <archivo>   uno o mas ficheros a escanear (los inexistentes se ignoran:
              si ninguno tiene IDs, el siguiente es <prefijo>-001).
  --width N   ancho de padding con ceros (default 3 → B-001).

Salida: el siguiente ID (p. ej. `B-004`) y exit 0. Exit 1 en error de uso.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def next_id(prefix: str, texts, width: int = 3) -> str:
    """Siguiente ID libre del prefijo escaneando todos los textos."""
    # (?<![A-Za-z0-9]) impide que el prefijo matchee como sufijo de otro token
    # (RF- vs F-, CR- vs R-). El prefijo es literal (puede llevar guion: F-C).
    rx = re.compile(r"(?<![A-Za-z0-9])" + re.escape(prefix) + r"-(\d+)\b")
    used = [int(n) for t in texts for n in rx.findall(t)]
    nxt = (max(used) + 1) if used else 1
    return f"{prefix}-{nxt:0{width}d}"


def main() -> int:
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("prefix")
    p.add_argument("files", nargs="+")
    p.add_argument("--width", type=int, default=3)
    try:
        args = p.parse_args()
    except SystemExit:
        return 1

    if args.width < 1:
        print("ERROR: --width debe ser >= 1", file=sys.stderr)
        return 1

    texts = []
    for f in args.files:
        path = Path(f)
        if path.exists():
            try:
                texts.append(path.read_text(encoding="utf-8"))
            except OSError as e:
                print(f"ERROR: no se puede leer {path}: {e}", file=sys.stderr)
                return 1

    print(next_id(args.prefix, texts, args.width))
    return 0


if __name__ == "__main__":
    sys.exit(main())
