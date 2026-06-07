#!/usr/bin/env python3
"""Sellador determinista de artefactos SDD (Fase 1.2 del ROADMAP).

Separa el AUTOR del SELLADOR: el agente auditor emite su veredicto experto,
pero el estado operativo (`Estado: BORRADOR|VALIDADO`) solo lo escribe este
script, y solo si las condiciones verificables mecanicamente se cumplen.
Un veredicto `OK` de un agente ya no es suficiente para sellar.

Uso:
    sdd-seal.py plan <plan.md> --check    # verifica condiciones, no escribe
    sdd-seal.py plan <plan.md> --seal     # verifica y sella VALIDADO si pasa
    sdd-seal.py plan <plan.md> --unseal   # fuerza Estado: BORRADOR (downgrade siempre permitido)

Exit codes: 0 = OK / sellado; 1 = error de uso o IO; 2 = condiciones no cumplidas.

Condiciones verificadas para `plan`:
  1. El archivo parece un Plan SDD (tiene linea `Estado:` y `Checklist de Trazabilidad`).
  2. Las 4 lineas de gaps del footer existen y todas dicen `ninguno`
     (DESIGN_GAPs, TECH_GAPs, TRACE_GAPs, PLAN_GAPs).
  3. El plan no contiene marcadores `[INCOMPLETO]`.
  4. El header `Spec origen` resuelve a un archivo legible.
  5. El spec origen no contiene `[INCOMPLETO]`, gaps `[CRÍTICO]` ni CAs `[INFERIDO]`.
  6. Si el spec declara `status_sync`, su valor es `in_sync`.
  6b. Si el spec declara `derived_from_prd_hash` y su PRD origen es resoluble,
      el hash actual del PRD coincide (sin deriva PRD→spec; ver sdd-sync-check.py).
  7. Trazabilidad: todo CA-XXX definido en el spec (encabezados `### CA-XXX`)
     aparece referenciado en el plan.

El sello es una marca operativa confiable (kb-plan-expert, "Estados del Plan"):
si cualquier condicion falla, el plan queda/vuelve a BORRADOR.
"""
import hashlib
import re
import sys
from pathlib import Path

GAP_LINES = ("DESIGN_GAPs", "TECH_GAPs", "TRACE_GAPs", "PLAN_GAPs")
# Tolera variantes de formato: `Estado: X`, `**Estado:** X`, `**Estado**: X`,
# `- Estado: X`, `**Estado: X**` — preservando el formato al reescribir.
ESTADO_RE = re.compile(
    r"^(?P<prefix>\s*(?:[-*>]\s*)?\**Estado:?\**\s*:?\s*)(?P<value>BORRADOR|VALIDADO)(?P<suffix>\s*\**\s*)$",
    re.MULTILINE,
)
SPEC_ORIGEN_RE = re.compile(r"Spec origen(?:\*\*)?\s*:?\**\s*`?(?P<path>[^`\s|]+)`?", re.IGNORECASE)
CA_DEF_RE = re.compile(r"^#{2,4}\s*(?P<ca>CA-\d{3,4})\b", re.MULTILINE)


def fail_usage(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    print(__doc__.split("Uso:")[1].split("Exit codes:")[0], file=sys.stderr)
    return 1


def check_plan(plan_path: Path):
    """Devuelve (checks, sellable) donde checks es lista de (ok, descripcion)."""
    checks = []

    def add(ok, desc):
        checks.append((ok, desc))
        return ok

    try:
        plan = plan_path.read_text(encoding="utf-8")
    except OSError as e:
        add(False, f"No se puede leer el plan: {e}")
        return checks, False

    # 1. Estructura minima de Plan SDD
    estado_m = ESTADO_RE.search(plan)
    add(estado_m is not None, "Linea `Estado:` presente con valor BORRADOR|VALIDADO")
    add("Checklist de Trazabilidad" in plan, "Seccion `Checklist de Trazabilidad` presente")

    # 2. Footer de gaps: las 4 lineas existen y dicen `ninguno`
    for gap in GAP_LINES:
        m = re.search(rf"^\*\*{gap}:\*\*\s*(?P<val>.*)$", plan, re.MULTILINE)
        if m is None:
            add(False, f"Linea `**{gap}:**` ausente del footer")
        else:
            val = m.group("val").strip().rstrip(".")
            add(val.lower() == "ninguno", f"`**{gap}:**` sin gaps abiertos (valor: '{val}')")

    # 3. Sin [INCOMPLETO] en el plan
    n_inc = len(re.findall(r"\[INCOMPLETO\]", plan))
    add(n_inc == 0, f"Plan sin marcadores [INCOMPLETO] (encontrados: {n_inc})")

    # 4. Spec origen resoluble
    spec_m = SPEC_ORIGEN_RE.search(plan)
    spec_text = None
    if not add(spec_m is not None, "Header `Spec origen` presente"):
        return checks, False
    spec_path = (plan_path.parent / spec_m.group("path")).resolve() \
        if not Path(spec_m.group("path")).is_absolute() else Path(spec_m.group("path"))
    try:
        spec_text = spec_path.read_text(encoding="utf-8")
        add(True, f"Spec origen legible: {spec_path}")
    except OSError:
        add(False, f"Spec origen NO legible: {spec_path}")
        return checks, False

    # 5. Spec sin [INCOMPLETO], [CRÍTICO] ni [INFERIDO] abiertos
    n_spec_inc = len(re.findall(r"\[INCOMPLETO\]", spec_text))
    add(n_spec_inc == 0, f"Spec sin [INCOMPLETO] (encontrados: {n_spec_inc})")
    n_spec_crit = len(re.findall(r"\[CR[IÍ]TICO\]", spec_text))
    add(n_spec_crit == 0, f"Spec sin gaps [CRÍTICO] (encontrados: {n_spec_crit})")
    n_spec_inf = len(re.findall(r"\[INFERIDO\]", spec_text))
    add(n_spec_inf == 0, f"Spec sin CAs [INFERIDO] sin confirmar (encontrados: {n_spec_inf})")

    # 6. status_sync del spec (si declarado) debe ser in_sync
    sync_m = re.search(r"status_sync\s*:\s*[\"']?(\w+)", spec_text)
    if sync_m:
        add(sync_m.group(1) == "in_sync", f"Spec `status_sync: {sync_m.group(1)}` (requerido: in_sync)")

    # 6b. Deriva PRD→spec por hash sellado (SSoT del mecanismo: sdd-sync-check.py).
    # Solo se evalua con evidencia completa: sello declarado + PRD origen resoluble.
    hash_m = re.search(r"derived_from_prd_hash\s*:\s*sha256:([0-9a-fA-F]{8,64})", spec_text)
    prd_m = re.search(r"derived_from_prd\s*:\s*`?([^`\s|]+)", spec_text)
    if hash_m and prd_m and prd_m.group(1).upper() not in ("N/A", "UNKNOWN"):
        prd_p = Path(prd_m.group(1))
        candidates = [prd_p] if prd_p.is_absolute() else [spec_path.parent / prd_p, prd_p]
        for c in candidates:
            try:
                prd_text = c.read_text(encoding="utf-8")
            except OSError:
                continue
            digest = hashlib.sha256(prd_text.replace("\r\n", "\n").encode("utf-8")).hexdigest()
            in_sync = digest.startswith(hash_m.group(1).lower())
            add(in_sync, f"Spec sin deriva respecto a su PRD origen ({c})" if in_sync
                else f"El PRD origen ({c}) cambió desde que se sincronizó el spec — resincroniza con /wf-spec-sync-from-prd")
            break

    # 7. Cobertura de CAs: todo CA definido en el spec aparece en el plan
    spec_cas = sorted(set(CA_DEF_RE.findall(spec_text)))
    if spec_cas:
        missing = [ca for ca in spec_cas if not re.search(rf"\b{ca}\b", plan)]
        add(not missing,
            f"Cobertura de CAs del spec en el plan ({len(spec_cas) - len(missing)}/{len(spec_cas)}"
            + (f"; sin cubrir: {', '.join(missing)}" if missing else "") + ")")
    else:
        add(False, "El spec no define ningun CA (`### CA-XXX`) — trazabilidad imposible")

    sellable = all(ok for ok, _ in checks)
    return checks, sellable


def write_estado(plan_path: Path, new_state: str) -> bool:
    text = plan_path.read_text(encoding="utf-8")
    m = ESTADO_RE.search(text)
    if m is None:
        print("ERROR: no se encuentra la linea `Estado:` para escribir el sello", file=sys.stderr)
        return False
    if m.group("value") == new_state:
        print(f"Estado ya era {new_state}; sin cambios.")
        return True
    new_text = text[:m.start()] + m.group("prefix") + new_state + m.group("suffix") + text[m.end():]
    plan_path.write_text(new_text, encoding="utf-8")
    print(f"Estado: {m.group('value')} → {new_state} escrito en {plan_path}")
    return True


def main() -> int:
    args = sys.argv[1:]
    if len(args) != 3 or args[0] != "plan" or args[2] not in ("--check", "--seal", "--unseal"):
        return fail_usage("argumentos invalidos")
    plan_path = Path(args[1])
    mode = args[2]

    if mode == "--unseal":
        # Downgrade siempre permitido: volver a BORRADOR es la direccion segura.
        return 0 if write_estado(plan_path, "BORRADOR") else 1

    checks, sellable = check_plan(plan_path)
    print(f"=== sdd-seal plan {'(check)' if mode == '--check' else '(seal)'} — {plan_path} ===")
    for ok, desc in checks:
        print(f"  {'✓' if ok else '✗'} {desc}")
    if not sellable:
        print("RESULTADO: condiciones NO cumplidas — el plan no es sellable. Estado queda/vuelve a BORRADOR.")
        if mode == "--seal":
            write_estado(plan_path, "BORRADOR")
        return 2

    if mode == "--check":
        print("RESULTADO: condiciones cumplidas — el plan es sellable.")
        return 0

    return 0 if write_estado(plan_path, "VALIDADO") else 1


if __name__ == "__main__":
    sys.exit(main())
