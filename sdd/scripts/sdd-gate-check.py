#!/usr/bin/env python3
"""Gate mecanico PreToolUse del pipeline SDD (Fase 1.1 del ROADMAP).

Se registra como hook PreToolUse (matcher: Skill) en el settings.json del
proyecto. Antes de que el orquestador invoque una wf-* con gate, verifica las
precondiciones POR CONTENIDO (no por existencia) y deniega la invocacion si
no se cumplen. Convierte los "obligatorio" de la prosa en bloqueos reales.

Protocolo: recibe el JSON del hook por stdin; si el gate falla, emite el JSON
de decision `permissionDecision: deny` con motivo accionable y sale 0. Si todo
pasa (o no aplica), no emite nada y sale 0.

Politica conservadora: solo se bloquea con evidencia positiva de violacion.
Si los argumentos no permiten resolver el artefacto (path ausente/ambiguo),
se PERMITE — el gate es una red de seguridad, no un parser de toda sintaxis;
las validaciones de prosa del workflow siguen aplicando.

Gates (tabla GATES):
  wf-prepare-tasks            → el `*_plan.md` del arg debe tener `Estado: VALIDADO`
                                y sin `Enmienda pendiente` (ver sdd-amend.py)
  wf-prepare-plan             → el `*_spec.md` del arg sin [INCOMPLETO]/[CRITICO], status_sync fiable
                                y sin deriva PRD→spec (hash sellado por sdd-sync-check.py)
  wf-design-system            → idem sobre el spec de entrada
  wf-design-feature-prototype → idem sobre el spec de entrada
  wf-task-run                 → el `Plan origen` del `*_tasks.md` sigue `Estado: VALIDADO`;
                                con `--task T-00X`, la task no referencia (Spec CA) un CA
                                con `Enmienda pendiente` en el plan (retencion selectiva)
  wf-qa-plan                  → idem gate de spec fiable (un QA plan de un spec inestable nace muerto)

Retirada de feature (D-074): un spec con `Estado: RETIRADO` deniega los tres frentes
—planificar, generar tasks y ejecutarlas—, resolviendo el `Spec origen` del plan y el
`Plan origen` del tasks. A diferencia de `Enmienda pendiente`, que retiene SOLO las
tasks que citan el CA enmendado, la baja cancela la feature entera: no queda
subconjunto que siga teniendo sentido ejecutar.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ESTADO_RE = re.compile(
    r"^\s*(?:[-*>]\s*)?\**Estado:?\**\s*:?\s*(?P<value>BORRADOR|VALIDADO|RETIRADO)\s*\**\s*$",
    re.MULTILINE,
)
SPEC_ORIGEN_RE = re.compile(r"Spec origen(?:\*\*)?\s*:?\**\s*`?(?P<path>[^`\s|]+)`?",
                            re.IGNORECASE)
# Anotacion de enmienda pendiente en el plan (unico escritor: sdd-amend.py)
AMEND_RE = re.compile(
    r"^[ \t]*(?:[-*>][ \t]*)?\**Enmienda pendiente:?\**[ \t]*:?[ \t]*"
    r"(?P<ca>CA-\d{3,4})[ \t]*\([ \t]*(?P<ref>E-\d{3,4})[^)\n]*\)[ \t]*$",
    re.MULTILINE,
)


def find_md_arg(args: str, marker: str):
    """Primer token .md cuyo nombre contiene el marcador (p. ej. '_plan')."""
    for token in re.findall(r"[^\s\"']+\.md", args or ""):
        if marker in Path(token).name:
            return Path(token)
    return None


def read(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def spec_origen_retirado(text: str, base: Path):
    """Devuelve el path del `Spec origen` si esta RETIRADO; None en cualquier otro caso.

    Politica conservadora del hook: si el header no esta, no resuelve o no es legible,
    NO se bloquea — el gate es una red de seguridad, no un parser de toda sintaxis.
    """
    m = SPEC_ORIGEN_RE.search(text)
    if m is None:
        return None
    sp = Path(m.group("path"))
    if not sp.is_absolute():
        sp = (base.parent / sp).resolve()
    spec_text = read(sp)
    if spec_text is None:
        return None
    e = ESTADO_RE.search(spec_text)
    return sp if e and e.group("value") == "RETIRADO" else None


def gate_plan_validado(args: str):
    plan_path = find_md_arg(args, "_plan")
    if plan_path is None:
        return None  # sin path resoluble → permitir (politica conservadora)
    text = read(plan_path)
    if text is None:
        return f"El plan '{plan_path}' no existe o no es legible. Pide que se genere el plan de esa feature antes de continuar."
    m = ESTADO_RE.search(text)
    if m is None:
        return f"'{plan_path}' no tiene linea `Estado:` reconocible — no parece un plan SDD sellable. Pide que se valide el plan primero."
    retirado = spec_origen_retirado(text, plan_path)
    if retirado:
        return (f"El spec origen de '{plan_path}' esta RETIRADO ('{retirado}'): esa feature se dio "
                f"de baja y ya no forma parte del producto. No generes tasks para construirla.")
    if m.group("value") != "VALIDADO":
        return f"El plan '{plan_path}' esta en Estado: {m.group('value')}. Pide que se valide el plan y resuelve sus hallazgos antes de generar tasks."
    amends = AMEND_RE.findall(text)
    if amends:
        detail = ", ".join(f"{ca} ({ref})" for ca, ref in amends)
        return (f"El plan '{plan_path}' tiene enmienda(s) pendiente(s) de revision: {detail}. "
                f"Cierra la revision scoped que dejo indicada la enmienda del CA, o pide una re-validacion del plan, antes de generar tasks.")
    return None


def prd_drift(spec_path: Path, spec_text: str):
    """Deriva PRD→spec por hash sellado (SSoT del mecanismo: sdd-sync-check.py).

    Devuelve mensaje si el spec declara `derived_from_prd_hash` y el PRD origen
    resoluble ya no coincide. Conservador: sin sello, PRD N/A o no resoluble →
    None (no bloquear).
    """
    h = re.search(r"derived_from_prd_hash\s*:\s*sha256:([0-9a-fA-F]{8,64})", spec_text)
    if h is None:
        return None
    # `derived_from_prd:` exige `:` tras "prd" — no matchea _version ni _hash
    p = re.search(r"derived_from_prd\s*:\s*`?([^`\s|]+)", spec_text)
    if p is None or p.group(1).upper() in ("N/A", "UNKNOWN"):
        return None
    prd = Path(p.group(1))
    candidates = [prd] if prd.is_absolute() else [spec_path.parent / prd, prd]
    for c in candidates:
        prd_text = read(c)
        if prd_text is None:
            continue
        digest = hashlib.sha256(prd_text.replace("\r\n", "\n").encode("utf-8")).hexdigest()
        if digest.startswith(h.group(1).lower()):
            return None
        return (f"el PRD origen '{c}' cambió desde que se generó/sincronizó el spec "
                f"(deriva detectada por hash). Pide que se mida el impacto del cambio de PRD "
                f"y que se resincronicen las specs, antes de continuar.")
    return None  # PRD no resoluble → permitir (política conservadora)


GAP_CRIT_RE = re.compile(r"^#{2,4}\s*\[(?P<id>[PD]-\d{3,4})\]\s*\[CR[IÍ]TICO\]", re.MULTILINE)
PENDIENTE_RE = re.compile(r"\*\*Respuesta\*\*\s*:\s*_\(pendiente\)_")


def open_critical_gaps(text: str):
    """Gaps `[CRITICO]` del propio spec que siguen SIN responder (D-061).

    Contar ocurrencias crudas de `[CRITICO]` bloquearia el spec para siempre:
    desde D-054 un spec conserva en `## Items Pendientes` el bloque de sus gaps
    criticos **tambien despues de responderlos**, por trazabilidad. Lo que
    bloquea es `Respuesta: _(pendiente)_`, no la palabra.
    """
    heads = list(GAP_CRIT_RE.finditer(text))
    abiertos = []
    for n, m in enumerate(heads):
        end = heads[n + 1].start() if n + 1 < len(heads) else len(text)
        nxt = re.search(r"^#{1,4}\s", text[m.end():end], re.MULTILINE)
        block = text[m.end():m.end() + nxt.start()] if nxt else text[m.end():end]
        if PENDIENTE_RE.search(block):
            abiertos.append(m.group("id"))
    return abiertos


def gate_spec_fiable(args: str):
    # Nota: el DESIGN_BRIEF.md no se verifica aqui (su ubicacion es ambigua
    # desde los args); ese gate sigue siendo de la prosa del workflow.
    spec_path = find_md_arg(args, "_spec")
    if spec_path is None:
        return None
    text = read(spec_path)
    if text is None:
        return f"El spec '{spec_path}' no existe o no es legible."
    # La baja se reporta primero: un spec retirado puede tener ademas gaps abiertos, y
    # decir "responde estos 3 criticos" sobre una feature cancelada manda a trabajar
    # en lo que ya no existe.
    m_ret = ESTADO_RE.search(text)
    if m_ret and m_ret.group("value") == "RETIRADO":
        ret = re.search(r"^\s*(?:[-*>]\s*)?\**Retirada:?\**\s*:?\s*(?P<v>[^\n]*)$",
                        text, re.MULTILINE)
        detalle = f" ({ret.group('v').strip()})" if ret and ret.group("v").strip() else ""
        return (f"El spec '{spec_path}' esta RETIRADO{detalle}: esa feature se dio de baja y ya "
                f"no forma parte del producto. Si la decision cambio, hay que reactivarla antes.")
    n_inc = len(re.findall(r"\[INCOMPLETO\]", text))
    if n_inc:
        return f"El spec '{spec_path}' tiene {n_inc} HU(s) [INCOMPLETO]. Responde los gaps que las bloquean —en el `_analysis.md` o en la seccion `Items Pendientes` del propio spec, segun donde esten definidos— y pide que se completen esas historias."
    # Gaps criticos: bloquean los ABIERTOS, no la palabra (D-061). Desde D-054 un
    # spec conserva el bloque de un critico ya respondido, y contarlo en crudo lo
    # dejaria insellable para siempre.
    n_raw = len(re.findall(r"\[CR[IÍ]TICO\]", text))
    heads = GAP_CRIT_RE.findall(text)
    if n_raw > len(heads):
        # Hay marcas [CRITICO] fuera de un bloque reconocible: no se puede
        # concluir que esten respondidas (guarda de D-037 — no declarar limpio
        # lo que no se ha sabido parsear).
        return (f"El spec '{spec_path}' tiene marcas [CRITICO] que no estan en un bloque de gap "
                f"con la forma `### [P-XXX][CRITICO]` (kb-gap-conventions). No se puede verificar "
                f"si estan respondidas: dale la forma canonica o resuelvelas antes de continuar.")
    abiertos = open_critical_gaps(text)
    if abiertos:
        return (f"El spec '{spec_path}' tiene {len(abiertos)} gap(s) [CRITICO] sin responder "
                f"({', '.join(abiertos)}). Respondelos donde estan definidos y pide que se "
                f"completen las historias afectadas.")
    n_inf = len(re.findall(r"\[INFERIDO\]", text))
    if n_inf:
        return (f"El spec '{spec_path}' tiene {n_inf} CA(s) [INFERIDO] sin confirmar (caracterizacion brownfield). "
                f"Confirmalos uno a uno antes de construir nada encima.")
    # Bloquean solo los estados con evidencia de desalineacion (kb-traceability-rules,
    # Regla 8). `unknown` es legitimo en specs sin PRD (fast-track directo) y la
    # deriva real con PRD la caza el check de hash de abajo.
    sync = re.search(r"status_sync\s*:\s*[\"']?(\w+)", text)
    if sync and sync.group(1) in ("stale", "needs_review"):
        return f"El spec '{spec_path}' declara status_sync: {sync.group(1)} (no fiable). Pide que se resincronice con el PRD antes de continuar."
    drift = prd_drift(spec_path, text)
    if drift:
        return f"El spec '{spec_path}' está desincronizado: {drift}"
    # Estado del spec (D-061): cada fase consume artefactos sellados de la anterior.
    # Solo se exige si el spec DECLARA el estado — un spec legacy sin la linea no
    # se bloquea (misma politica conservadora que `status_sync`).
    estado = m_ret
    if estado and estado.group("value") == "BORRADOR":
        return (f"El spec '{spec_path}' esta en BORRADOR: nadie lo ha validado todavia. "
                f"Pide que se valide antes de planificar sobre el.")
    return None


def gate_tasks_plan_vigente(args: str):
    """wf-task-run: el plan referenciado por `Plan origen` del _tasks.md sigue VALIDADO."""
    tasks_path = find_md_arg(args, "_tasks")
    if tasks_path is None:
        return None
    text = read(tasks_path)
    if text is None:
        return f"El tasks '{tasks_path}' no existe o no es legible. Pide que se generen las tasks de esa feature primero."
    m = re.search(r"Plan origen(?:\*\*)?\s*:?\**\s*`?(?P<path>[^`\s|]+)`?", text, re.IGNORECASE)
    if m is None:
        return None  # sin header resoluble → permitir (politica conservadora)
    plan_path = Path(m.group("path"))
    if not plan_path.is_absolute():
        plan_path = (tasks_path.parent / plan_path).resolve()
    plan_text = read(plan_path)
    if plan_text is None:
        return f"El `Plan origen` de '{tasks_path}' no resuelve ('{plan_path}'). Corrige el header antes de ejecutar tasks."
    retirado = spec_origen_retirado(plan_text, plan_path)
    if retirado:
        return (f"El spec origen de '{plan_path}' esta RETIRADO ('{retirado}'): la feature se dio "
                f"de baja. No se ejecuta ninguna de sus tasks — a diferencia de una enmienda, que "
                f"retiene solo las del CA afectado, aqui no queda nada que construir.")
    pm = ESTADO_RE.search(plan_text)
    if pm and pm.group("value") != "VALIDADO":
        return (f"El plan origen '{plan_path}' esta en Estado: {pm.group('value')} — fue degradado tras generar las tasks. "
                f"Pide que se valide el plan antes de ejecutar tasks.")

    # Retencion selectiva por enmienda (sdd-amend.py): si la invocacion apunta a
    # una task concreta (--task T-00X) y esa task referencia (Spec CA) un CA con
    # `Enmienda pendiente` en el plan, se deniega SOLO esa task; el resto de la
    # feature sigue ejecutable. Sin --task no se bloquea aqui: `sdd-task-state.py
    # next` salta las retenidas de forma determinista.
    amends = {ca: ref for ca, ref in AMEND_RE.findall(plan_text)}
    task_m = re.search(r"--task\s+(?P<id>T-\d{3,4})\b", args or "")
    if amends and task_m:
        task_id = task_m.group("id")
        block_m = re.search(rf"^##\s+{task_id}\s*:.*?(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL)
        if block_m:
            ca_line = re.search(r"^\s*(?:[-*>]\s*)?\**Spec CA:?\**\s*:?\s*(?P<cas>.+)$",
                                block_m.group(0), re.MULTILINE | re.IGNORECASE)
            if ca_line:
                task_cas = set(re.findall(r"CA-\d{3,4}", ca_line.group("cas")))
                held = sorted(task_cas & set(amends))
                if held:
                    detail = ", ".join(f"{ca} ({amends[ca]})" for ca in held)
                    return (f"la task {task_id} esta retenida por enmienda pendiente sobre {detail}. "
                            f"Revisa la seccion del plan que cubre ese CA y limpia la anotacion "
                            f"(sdd-amend.py clear) o pide una re-validacion del plan.")
    return None


GATES = {
    "wf-prepare-tasks": gate_plan_validado,
    "wf-prepare-plan": gate_spec_fiable,
    "wf-design-system": gate_spec_fiable,
    "wf-design-feature-prototype": gate_spec_fiable,
    "wf-task-run": gate_tasks_plan_vigente,
    "wf-qa-plan": gate_spec_fiable,
}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # stdin ilegible → no interferir

    if payload.get("tool_name") != "Skill":
        return 0
    tool_input = payload.get("tool_input") or {}
    skill = (tool_input.get("skill") or "").strip()
    args = tool_input.get("args") or ""

    gate = GATES.get(skill)
    if gate is None:
        return 0

    try:
        reason = gate(args)
    except Exception:
        return 0  # error interno del gate → no bloquear el pipeline

    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"[SDD-GATE] {skill}: {reason}",
            }
        }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
