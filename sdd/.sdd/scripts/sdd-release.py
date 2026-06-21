#!/usr/bin/env python3
# sdd-version: 0.37.0+3cdfd2d
"""Noción mínima de release: vincula el cierre de una feature a un SHA/tag (ROADMAP 2.7).

El pipeline cerraba el ciclo en el `_qa_report.md` con veredicto APTO, pero la
trazabilidad terminaba ahí: nada registraba EN QUÉ punto de producción (commit
SHA / tag) se entregó la feature. Este script añade el último eslabón de la
cadena CA → TC → task → commit → **release**.

Principios (los mismos que el sellador y task-state):
  - **Verdad mecánica**: el SHA lo da `git rev-parse`, no el agente — no puede
    mentir ni derivar. El tag es opcional y declarativo (lo elige el humano).
  - **Gate de cierre**: una feature no se "releasa" si su QA no pasó. El script
    rechaza (exit 2) si el `_qa_report.md` no existe o su veredicto es NO_APTO.
    APTO y APTO_CON_RESERVAS se permiten; el veredicto real queda grabado en la
    entrada (honestidad: releasar con reservas se documenta como tal).
  - **Único escritor**: el campo de release (`<n>_release.md`) solo lo escribe
    este script. Re-releases (hotfix tras bug) se acumulan como R-001, R-002…

Uso:
    sdd-release.py stamp <feature_dir> [--tag <tag>] [--sha <sha>] [--date <YYYY-MM-DD>] [--note <texto>]
    sdd-release.py check <feature_dir>

<feature_dir> es la carpeta de la feature (contiene `tasks/` o, en layout plano
legacy, los artefactos directamente). Exit 0 = ok; 1 = error de uso; 2 = gate
rechazado (sin QA APTO).
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import date as _date
from pathlib import Path

RELEASE_RE = re.compile(r"^##\s+R-(\d+)\b", re.MULTILINE)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def first(directory: Path, *patterns: str) -> Path | None:
    for pat in patterns:
        matches = sorted(directory.glob(pat))
        if matches:
            return matches[0]
    return None


def header_field(text: str, key: str) -> str | None:
    m = re.search(r"^>\s*\**" + re.escape(key) + r"\**\s*:\s*(.*)$", text, re.MULTILINE)
    return m.group(1).strip().strip("`") if m else None


def qa_verdict(text: str) -> str:
    for v in ("NO_APTO", "APTO_CON_RESERVAS", "APTO"):
        if v in text:
            return v
    return "?"


def git_sha(cwd: Path) -> tuple[str, str] | None:
    """(sha_completo, sha_corto) del HEAD, o None si no hay repo git."""
    try:
        full = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        short = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return (full, short) if full else None
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def resolve_artifacts(fdir: Path) -> tuple[Path | None, Path | None, Path]:
    """Devuelve (qa_report, spec, release_path) respetando subcarpetas y layout plano."""
    qa = first(fdir, "tasks/*_qa_report.md", "*_qa_report.md")
    spec = first(fdir, "spec/*_spec.md", "*_spec.md")
    # El release vive junto al qa_report (misma carpeta y mismo basename de feature).
    if qa:
        base = qa.name[: -len("_qa_report.md")]
        release_path = qa.parent / f"{base}_release.md"
    else:
        base = fdir.name
        subdir = fdir / "tasks"
        parent = subdir if subdir.is_dir() else fdir
        release_path = parent / f"{base}_release.md"
    return qa, spec, release_path


def feature_id(spec: Path | None, fallback: str) -> str:
    if spec:
        fid = header_field(read_text(spec), "Feature ID")
        if fid:
            return fid
    return fallback


def next_release_id(release_text: str) -> str:
    nums = [int(m) for m in RELEASE_RE.findall(release_text)]
    return f"R-{(max(nums) + 1 if nums else 1):03d}"


def cmd_check(fdir: Path) -> int:
    _, _, release_path = resolve_artifacts(fdir)
    if not release_path.exists():
        sys.stdout.write(f"SIN_RELEASE: {fdir.name} no tiene release registrado.\n")
        return 0
    text = read_text(release_path)
    entries = RELEASE_RE.findall(text)
    last = f"R-{int(max(entries, key=int)):03d}" if entries else "?"
    sys.stdout.write(f"RELEASED: {fdir.name} — {len(entries)} release(s), último {last}\n")
    sys.stdout.write(f"  archivo: {release_path}\n")
    return 0


def cmd_stamp(fdir: Path, tag: str | None, sha_arg: str | None,
              date_arg: str | None, note: str | None) -> int:
    qa, spec, release_path = resolve_artifacts(fdir)

    # ── Gate de cierre: sin QA APTO no hay release ──
    if not qa:
        sys.stderr.write(
            f"[release] RECHAZADO: {fdir.name} no tiene `_qa_report.md`. "
            "Cierra el ciclo QA con /wf-qa-verify antes de releasar.\n"
        )
        return 2
    verdict = qa_verdict(read_text(qa))
    if verdict not in ("APTO", "APTO_CON_RESERVAS"):
        sys.stderr.write(
            f"[release] RECHAZADO: veredicto QA de {fdir.name} es '{verdict}' "
            "(se requiere APTO o APTO_CON_RESERVAS). Resuelve el QA y re-verifica.\n"
        )
        return 2

    # ── SHA mecánico (no lo teclea el agente) ──
    if sha_arg:
        sha_full, sha_short = sha_arg, sha_arg[:9]
    else:
        sha = git_sha(fdir)
        if sha is None:
            sys.stderr.write(
                f"[release] RECHAZADO: {fdir.name} no está en un repo git y no se pasó "
                "--sha. El release necesita un punto verificable de producción.\n"
            )
            return 2
        sha_full, sha_short = sha

    fid = feature_id(spec, fdir.name)
    stamp_date = date_arg or _date.today().isoformat()

    existing = read_text(release_path) if release_path.exists() else ""
    rid = next_release_id(existing)

    entry = [
        f"## {rid} — {stamp_date}",
        f"- **Commit/SHA:** `{sha_full}` (`{sha_short}`)",
        f"- **Tag:** {('`' + tag + '`') if tag else '—'}",
        f"- **Veredicto QA:** {verdict}",
        f"- **Basado en:** {qa.name}",
    ]
    if note:
        entry.append(f"- **Nota:** {note}")
    entry.append("")
    entry_text = "\n".join(entry)

    if existing:
        # Inserta la nueva entrada tras el header, antes de la primera ## R- previa.
        m = RELEASE_RE.search(existing)
        if m:
            new_text = existing[: m.start()] + entry_text + "\n" + existing[m.start():]
        else:
            new_text = existing.rstrip() + "\n\n" + entry_text
    else:
        header = [
            f"# Release log — {fdir.name} ({fid})",
            f"> Feature: {fid}",
            "> Registro generado por `sdd-release.py` (único escritor del coordinador de release).",
            "",
            entry_text,
        ]
        new_text = "\n".join(header)

    release_path.parent.mkdir(parents=True, exist_ok=True)
    release_path.write_text(new_text if new_text.endswith("\n") else new_text + "\n",
                            encoding="utf-8")

    sys.stdout.write(
        f"[release] {rid} registrado para {fid}: {sha_short}"
        + (f" tag {tag}" if tag else "")
        + f" (QA {verdict})\n"
    )
    sys.stdout.write(f"  archivo: {release_path}\n")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in ("stamp", "check"):
        sys.stderr.write(
            "uso: sdd-release.py stamp <feature_dir> [--tag <tag>] [--sha <sha>] "
            "[--date <YYYY-MM-DD>] [--note <texto>]\n"
            "     sdd-release.py check <feature_dir>\n"
        )
        return 1
    mode = argv[0]

    def opt(name: str) -> str | None:
        if name in argv:
            i = argv.index(name)
            if i + 1 < len(argv):
                return argv[i + 1]
        return None

    positionals = []
    skip = False
    for i, a in enumerate(argv[1:], start=1):
        if skip:
            skip = False
            continue
        if a in ("--tag", "--sha", "--date", "--note"):
            skip = True
            continue
        positionals.append(a)

    if not positionals:
        sys.stderr.write("[release] falta <feature_dir>\n")
        return 1
    fdir = Path(positionals[0]).resolve()
    if not fdir.is_dir():
        sys.stderr.write(f"[release] no es un directorio: {fdir}\n")
        return 1

    if mode == "check":
        return cmd_check(fdir)
    return cmd_stamp(fdir, opt("--tag"), opt("--sha"), opt("--date"), opt("--note"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
