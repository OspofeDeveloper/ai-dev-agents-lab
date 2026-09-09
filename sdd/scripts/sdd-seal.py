#!/usr/bin/env python3
"""Sellador determinista de artefactos SDD (Fase 1.2 del ROADMAP).

Separa el AUTOR del SELLADOR: el agente auditor emite su veredicto experto,
pero el estado operativo (`Estado: BORRADOR|VALIDADO`) solo lo escribe este
script, y solo si las condiciones verificables mecanicamente se cumplen.
Un veredicto `OK` de un agente ya no es suficiente para sellar.

Uso:
    sdd-seal.py <plan|spec> <archivo.md> --check    # verifica condiciones, no escribe
    sdd-seal.py <plan|spec> <archivo.md> --seal     # verifica y sella VALIDADO si pasa
    sdd-seal.py <plan|spec> <archivo.md> --seal --approved-by "Nombre (Rol) (fecha)"
                                                   # ademas estampa `Aprobado por:` (Regla 10)
    sdd-seal.py <plan|spec> <archivo.md> --unseal   # fuerza Estado: BORRADOR (downgrade siempre permitido)

Exit codes: 0 = OK / sellado; 1 = error de uso o IO; 2 = condiciones no cumplidas.

Condiciones verificadas para `plan`:
  1. El archivo parece un Plan SDD (tiene linea `Estado:` y `Checklist de Trazabilidad`).
  2. Las 4 lineas de gaps del footer existen y todas dicen `ninguno`
     (DESIGN_GAPs, TECH_GAPs, TRACE_GAPs, PLAN_GAPs).
  3. El plan no contiene marcadores `[INCOMPLETO]`.
  4. El header `Spec origen` resuelve a un archivo legible.
  5. El spec origen no contiene `[INCOMPLETO]`, gaps `[CRÍTICO]` ni CAs `[INFERIDO]`.
  6. Si el spec declara `status_sync`, no esta desalineado (bloquean: stale, needs_review;
     `unknown` es legitimo en specs sin PRD).
  6b. Si el spec declara `derived_from_prd_hash` y su PRD origen es resoluble,
      el hash actual del PRD coincide (sin deriva PRD→spec; ver sdd-sync-check.py).
  7. Trazabilidad: todo CA-XXX definido en el spec (encabezados `### CA-XXX`)
     aparece referenciado en el plan.
  8. Deuda tecnica (ROADMAP 3.2): si el plan declara entradas `### TD-XXX`,
     cada una tiene sus campos obligatorios completos (Decision, A pesar de,
     Riesgo asumido, Queda pendiente, Componentes afectados, Aprobada por) y
     ninguna queda `Aprobada por: PENDIENTE` — la deuda APROBADA no bloquea
     (esa es su razon de ser), la deuda sin aprobar bloquea como un gap.
     Sin entradas TD → la condicion no aplica.

Condiciones verificadas para `spec` (D-061):
  1. El archivo parece un Spec SDD (linea `Estado:` y al menos una HU o un CA).
  2. Ninguna HU marcada `[INCOMPLETO]`.
  3. Ningun gap `[CRITICO]` ABIERTO en su `## Items Pendientes` (un critico ya
     respondido no bloquea: lo que bloquea es `Respuesta: _(pendiente)_`).
  4. Ningun CA `[INFERIDO]` sin confirmar (caracterizacion brownfield).
  5. Si declara `status_sync`, no esta desalineado (bloquean: stale, needs_review).
  6. Si declara `derived_from_prd_hash` y su PRD origen es resoluble, sin deriva.
  7. Trazabilidad interna: todo `### CA-XXX` declara su HU padre (`← HU-XXX`).
  8b. Cabecera completa (D-066): declara `Feature ID` y `Origen de alcance`, los
      campos que `sdd-features-index.py`, `sdd-project-status.py` y `sdd-release.py`
      leen para derivar indice, estado de delivery y coordenada de release. Si
      faltan, esos scripts NO fallan: omiten la feature en silencio.
  8. Asunciones visibles (D-063): todo gap `[INFORMATIVO]` sin responder —cuya
     `Asuncion por defecto` YA esta aplicada en los CAs— deja su entrada en
     `## Asunciones Aplicadas` citando el gap. No se juzga si la asuncion es
     correcta (juicio semantico, no mecanizable): se exige que la decision
     tomada en nombre del usuario sea VISIBLE. Guarda de vacuidad: si la
     seccion existe pero no se le reconoce ninguna entrada `- **[A-00X]**`,
     se deniega en vez de darla por buena (D-037).

El sello es una marca operativa confiable (kb-plan-expert, "Estados del Plan"):
si cualquier condicion falla, el plan queda/vuelve a BORRADOR.

Enmiendas (ROADMAP 4.2): al sellar con --seal se limpian las anotaciones
`Enmienda pendiente` del plan (escritas por sdd-amend.py) — la re-validacion
completa verifica contra el spec vigente, que ya incorpora la enmienda, asi
que quedan absorbidas. `--check` nunca las toca ni bloquea por ellas.
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
# Entradas de deuda tecnica asumida (kb-plan-expert, "Deuda tecnica asumida")
TD_HEADER_RE = re.compile(r"^#{2,4}\s*(?P<td>TD-\d{3,4})\b", re.MULTILINE)
TD_FIELDS = ("Decisión", "A pesar de", "Riesgo asumido", "Queda pendiente",
             "Componentes afectados", "Aprobada por")
# Anotacion de enmienda pendiente (unico escritor: sdd-amend.py; absorbida al re-sellar)
# Atribucion de aprobacion humana (kb-traceability-rules Regla 10). El valor es un
# dato HUMANO —no verificable mecanicamente— pero quien lo estampa es el script, no
# el hilo principal: mismo reparto que en el PRD (`sdd-prd-apply.py --seal "<valor>"`),
# y asi main no escribe contenido en el artefacto ([[D-060]]). [[D-065]]
APROBADO_RE = re.compile(
    r"^(?P<prefix>\s*(?:[-*>]\s*)?\**Aprobado por:?\**\s*:?\s*)(?P<value>[^\n]*)$",
    re.MULTILINE)
AMEND_LINE_RE = re.compile(
    r"^[ \t]*(?:[-*>][ \t]*)?\**Enmienda pendiente:?\**[ \t]*:?[ \t]*"
    r"(?P<ca>CA-\d{3,4})[ \t]*\([ \t]*(?P<ref>E-\d{3,4})[^)\n]*\)[ \t]*$\n?",
    re.MULTILINE,
)


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

    # 6. status_sync del spec (si declarado) no debe estar desalineado.
    # Bloquean solo `stale` y `needs_review` (kb-traceability-rules, Regla 8);
    # `unknown` es legitimo en specs sin PRD (fast-track directo) y la deriva
    # real con PRD la caza el check 6b por hash.
    sync_m = re.search(r"status_sync\s*:\s*[\"']?(\w+)", spec_text)
    if sync_m:
        add(sync_m.group(1) not in ("stale", "needs_review"),
            f"Spec `status_sync: {sync_m.group(1)}` (bloquean: stale, needs_review)")

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
                else f"El PRD origen ({c}) cambió desde que se sincronizó el spec — pide que se resincronice antes de sellar")
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

    # 8. Deuda tecnica asumida: TDs completas y ninguna PENDIENTE (la deuda
    # aprobada NO bloquea — esa es su razon de ser; la no aprobada si).
    td_headers = list(TD_HEADER_RE.finditer(plan))
    for i, m in enumerate(td_headers):
        end = td_headers[i + 1].start() if i + 1 < len(td_headers) else len(plan)
        # El bloque de la TD termina en el siguiente encabezado de cualquier nivel
        next_h = re.search(r"^#{1,4}\s", plan[m.end():end], re.MULTILINE)
        block = plan[m.start():m.end() + next_h.start()] if next_h else plan[m.start():end]
        td = m.group("td")
        problems = []
        for field in TD_FIELDS:
            fm = re.search(rf"^\s*(?:[-*]\s*)?\**{field}:?\**\s*:?\s*(?P<val>.+?)\s*$",
                           block, re.MULTILINE)
            val = (fm.group("val") if fm else "").strip().strip("*").strip()
            if not val or re.fullmatch(r"\[.*\]|<.*>|\.{3}|…", val):
                problems.append(f"campo `{field}` ausente o sin rellenar")
            elif field == "Aprobada por" and val.upper().startswith("PENDIENTE"):
                problems.append("sin aprobacion humana (`Aprobada por: PENDIENTE`)")
        add(not problems,
            f"Deuda {td} completa y aprobada" if not problems
            else f"Deuda {td}: {'; '.join(problems)} — apruebala en /wf-plan-validate o conviertela en gap")

    sellable = all(ok for ok, _ in checks)
    return checks, sellable


GAP_CRIT_RE = re.compile(r"^#{2,4}\s*\[(?P<id>[PD]-\d{3,4})\]\s*\[CR[IÍ]TICO\]", re.MULTILINE)
PENDIENTE_RE = re.compile(r"\*\*Respuesta\*\*\s*:\s*_\(pendiente\)_")
CA_HU_RE = re.compile(r"^#{2,4}\s*(?P<ca>CA-\d{3,4})\b(?P<rest>[^\n]*)$", re.MULTILINE)
GAP_INFO_RE = re.compile(r"^#{2,4}\s*\[(?P<id>[PD]-\d{3,4})\]\s*\[INFORMATIVO\]", re.MULTILINE)
# `## Asunciones Aplicadas`, y la variante versionada que escribe wf-spec-delta:
# `## Asunciones Aplicadas (v1.1)`. Puede haber varias en un spec con historia.
ASUNCIONES_SEC_RE = re.compile(r"^#{2,3}[ \t]*Asunciones Aplicadas\b[^\n]*$", re.MULTILINE)
ASUNCION_ENTRY_RE = re.compile(r"^[ \t]*[-*][ \t]*\**\[(?P<id>A-\d{3,4})\]", re.MULTILINE)
GAP_REF_RE = re.compile(r"\b[PD]-\d{3,4}\b")


def _open_gaps(text: str, head_re):
    """IDs de los bloques de gap que casan `head_re` y siguen `_(pendiente)_`."""
    heads = list(head_re.finditer(text))
    open_ids = []
    for n, m in enumerate(heads):
        end = heads[n + 1].start() if n + 1 < len(heads) else len(text)
        nxt = re.search(r"^#{1,4}\s", text[m.end():end], re.MULTILINE)
        block = text[m.end():m.end() + nxt.start()] if nxt else text[m.end():end]
        if PENDIENTE_RE.search(block):
            open_ids.append(m.group("id"))
    return open_ids


def _open_critical_gaps(text: str):
    """IDs de gaps `[CRITICO]` del spec que siguen con `Respuesta: _(pendiente)_`.

    Un critico YA RESPONDIDO no bloquea el sello: su bloque se conserva por
    trazabilidad y la HU que bloqueaba ya esta completa. Lo que bloquea es la
    respuesta pendiente, no la palabra `[CRITICO]` (contar ocurrencias crudas
    dejaria el spec insellable para siempre).
    """
    return _open_gaps(text, GAP_CRIT_RE)


def _assumption_sections(text: str):
    """Cuerpo de cada `## Asunciones Aplicadas` del spec (puede haber varias)."""
    bodies = []
    for m in ASUNCIONES_SEC_RE.finditer(text):
        rest = text[m.end():]
        nxt = re.search(r"^#{1,2}[ \t]", rest, re.MULTILINE)
        bodies.append(rest[:nxt.start()] if nxt else rest)
    return bodies


def _undocumented_assumptions(text: str):
    """Asunciones aplicadas en nombre del usuario que no dejaron rastro (D-063).

    Un gap `[INFORMATIVO]` sin responder NO se queda sin decidir: se aplica su
    `Asuncion por defecto` y esa decision entra en los CAs como si alguien la
    hubiera elegido (kb-gap-conventions). Por eso tiene que dejar su entrada en
    `## Asunciones Aplicadas`, citando el gap del que sale.

    Es el analogo del invariante 1:1 del PRD (`sdd-prd-ready.py`), con la
    diferencia de que aqui la contrapartida ya existe en el formato actual —el
    bloque `[INFORMATIVO]`— y no hace falta inventar ninguna marca inline.

    No verifica que la asuncion sea correcta: eso es juicio semantico y no es
    mecanizable. Verifica que la decision es VISIBLE.

    Devuelve (ids_sin_rastro, seccion_ilegible).
    """
    aplicadas = _open_gaps(text, GAP_INFO_RE)
    if not aplicadas:
        return [], False

    bodies = _assumption_sections(text)
    if not bodies:
        return aplicadas, False

    # Guarda de vacuidad (D-037): la seccion esta, pero no se le reconoce
    # ninguna entrada `- **[A-00X]**`. No declares documentado lo que no has
    # sabido parsear — es el modo de fallo medido en la pasada 12 de CU-3.a,
    # donde unos gaps escritos como vinetas dejaron de existir para el script.
    if not any(ASUNCION_ENTRY_RE.search(b) for b in bodies):
        return aplicadas, True

    citados = {ref for b in bodies for ref in GAP_REF_RE.findall(b)}
    return [g for g in aplicadas if g not in citados], False


def check_spec(spec_path: Path):
    """Condiciones mecanicas para sellar un Spec como VALIDADO (D-061).

    Mismo reparto que en `plan`: el auditor emite el veredicto experto, pero el
    estado operativo lo escribe este script y solo si estas condiciones pasan.
    """
    checks = []

    def add(ok, desc):
        checks.append((bool(ok), desc))
        return bool(ok)

    try:
        text = spec_path.read_text(encoding="utf-8")
    except OSError as exc:
        add(False, f"No se puede leer el spec: {exc}")
        return checks, False

    # 1. Parece un Spec SDD.
    tiene_estado = ESTADO_RE.search(text) is not None
    tiene_cuerpo = re.search(r"^#{2,4}\s*(HU|CA)-\d{3,4}\b", text, re.MULTILINE) is not None
    if not add(tiene_estado and tiene_cuerpo,
               "El archivo parece un Spec SDD (linea `Estado:` + HUs/CAs)"):
        return checks, False

    # 2. HUs completas.
    n_inc = len(re.findall(r"\[INCOMPLETO\]", text))
    add(n_inc == 0, f"Sin HUs [INCOMPLETO] (encontradas: {n_inc})")

    # 3. Gaps criticos propios, abiertos.
    abiertos = _open_critical_gaps(text)
    add(not abiertos,
        "Sin gaps [CRÍTICO] abiertos en `Items Pendientes`"
        + (f" (abiertos: {', '.join(abiertos)})" if abiertos else ""))

    # 4. CAs confirmados.
    n_inf = len(re.findall(r"\[INFERIDO\]", text))
    add(n_inf == 0, f"Sin CAs [INFERIDO] sin confirmar (encontrados: {n_inf})")

    # 5. status_sync fiable (misma regla que en `plan`).
    sync_m = re.search(r"status_sync\s*:\s*[\"']?(\w+)", text)
    if sync_m:
        add(sync_m.group(1) not in ("stale", "needs_review"),
            f"`status_sync: {sync_m.group(1)}` (bloquean: stale, needs_review)")

    # 6. Sin deriva PRD->spec (misma evidencia que en `plan`).
    hash_m = re.search(r"derived_from_prd_hash\s*:\s*sha256:([0-9a-fA-F]{8,64})", text)
    prd_m = re.search(r"derived_from_prd\s*:\s*`?([^`\s|]+)", text)
    if hash_m and prd_m and prd_m.group(1).upper() not in ("N/A", "UNKNOWN"):
        prd_p = Path(prd_m.group(1))
        for c in ([prd_p] if prd_p.is_absolute() else [spec_path.parent / prd_p, prd_p]):
            try:
                prd_text = c.read_text(encoding="utf-8")
            except OSError:
                continue
            digest = hashlib.sha256(prd_text.replace("\r\n", "\n").encode("utf-8")).hexdigest()
            in_sync = digest.startswith(hash_m.group(1).lower())
            add(in_sync, f"Sin deriva respecto a su PRD origen ({c})" if in_sync
                else f"El PRD origen ({c}) cambió desde que se sincronizó el spec")
            break

    # 7. Trazabilidad interna: todo CA declara su HU padre.
    huerfanos = [m.group("ca") for m in CA_HU_RE.finditer(text)
                 if not re.search(r"HU-\d{3,4}", m.group("rest"))]
    if CA_HU_RE.search(text):
        add(not huerfanos,
            "Todo CA declara su HU padre"
            + (f" (sin padre: {', '.join(huerfanos)})" if huerfanos else ""))

    # 8b. La cabecera declara lo que los derivados leen (D-066).
    # Un campo ausente aqui no rompe nada de forma visible: `sdd-features-index.py`
    # simplemente no lo emite, y la feature aparece incompleta —o no aparece— en un
    # indice con apariencia de correcto. Es el modo de fallo que [[D-046]] declaro
    # inaceptable, y el analogo de `sdd-prd-frontmatter.py` en la fase PRD.
    faltan = [k for k in ("Feature ID", "Origen de alcance")
              if not re.search(r"^\s*>?\s*\**" + k + r"\**\s*:\s*\**\s*\S", text, re.MULTILINE)]
    add(not faltan,
        "La cabecera declara `Feature ID` y `Origen de alcance`"
        + (f" (faltan: {', '.join(faltan)})" if faltan else ""))

    # 8. Toda asuncion aplicada en nombre del usuario deja rastro (D-063).
    sin_rastro, ilegible = _undocumented_assumptions(text)
    if ilegible:
        add(False,
            "`## Asunciones Aplicadas` existe pero no se le reconoce ninguna entrada "
            "`- **[A-00X]**` — no se da por documentada una seccion que no se ha sabido "
            "parsear (ver D-037)")
    elif sin_rastro:
        add(False,
            "Toda asuncion aplicada deja rastro en `## Asunciones Aplicadas` "
            f"(sin entrada que los cite: {', '.join(sin_rastro)})")
    elif _open_gaps(text, GAP_INFO_RE):
        add(True, "Toda asuncion aplicada deja rastro en `## Asunciones Aplicadas`")

    return checks, all(ok for ok, _ in checks)


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


def write_aprobado(path: Path, valor: str) -> bool:
    """Estampa `Aprobado por: <valor>` en la cabecera; la crea junto a `Estado:` si falta.

    Solo se llama tras un sellado con exito: un artefacto que no pasa las condiciones
    no tiene aprobacion que registrar.
    """
    text = path.read_text(encoding="utf-8")
    m = APROBADO_RE.search(text)
    if m is not None:
        new_text = text[:m.start()] + m.group("prefix") + valor + text[m.end():]
    else:
        e = ESTADO_RE.search(text)
        if e is None:
            print("ERROR: no hay linea `Estado:` junto a la que estampar `Aprobado por:`",
                  file=sys.stderr)
            return False
        # La linea nueva se CALCA de la de `Estado:` (blockquote, bullet o negrita)
        # sustituyendo etiqueta y valor: asi hereda el formato exacto de la cabecera
        # sin tener que reconstruirlo, que es donde se rompia `**Estado:**`.
        # Ni `e.start()` ni `e.end()` sirven de ancla: el `^` de ESTADO_RE puede casar
        # en una linea en blanco anterior (su `\s*` se come el salto) y el `suffix`
        # puede comerse el de despues. La posicion fiable es la palabra `Estado`.
        pos = text.index("Estado", e.start())
        line_start = text.rfind("\n", 0, pos) + 1
        nl = text.find("\n", pos)
        end = len(text) if nl == -1 else nl
        estado_line = text[line_start:end]
        line = estado_line.replace("Estado", "Aprobado por", 1)
        line = line.replace(e.group("value"), valor, 1)
        new_text = text[:end] + "\n" + line + text[end:]
    path.write_text(new_text, encoding="utf-8")
    print(f"Aprobado por: {valor} — escrito en {path}")
    return True


def main() -> int:
    args = sys.argv[1:]
    aprobado = None
    if "--approved-by" in args:
        i = args.index("--approved-by")
        if i + 1 >= len(args):
            return fail_usage("`--approved-by` necesita un valor entre comillas")
        aprobado = args[i + 1]
        args = args[:i] + args[i + 2:]
    if (len(args) != 3 or args[0] not in ("plan", "spec")
            or args[2] not in ("--check", "--seal", "--unseal")):
        return fail_usage("argumentos invalidos")
    kind = args[0]
    plan_path = Path(args[1])
    mode = args[2]
    if aprobado is not None and mode != "--seal":
        return fail_usage("`--approved-by` solo aplica con `--seal`")

    if mode == "--unseal":
        # Downgrade siempre permitido: volver a BORRADOR es la direccion segura.
        return 0 if write_estado(plan_path, "BORRADOR") else 1

    checks, sellable = check_plan(plan_path) if kind == "plan" else check_spec(plan_path)
    print(f"=== sdd-seal {kind} {'(check)' if mode == '--check' else '(seal)'} — {plan_path} ===")
    for ok, desc in checks:
        print(f"  {'✓' if ok else '✗'} {desc}")
    if not sellable:
        print(f"RESULTADO: condiciones NO cumplidas — el {kind} no es sellable. Estado queda/vuelve a BORRADOR.")
        if mode == "--seal":
            write_estado(plan_path, "BORRADOR")
        return 2

    if mode == "--check":
        print(f"RESULTADO: condiciones cumplidas — el {kind} es sellable.")
        return 0

    # --seal: absorber enmiendas pendientes — la validacion completa que precede
    # al sellado ya audito el plan contra el spec vigente (con la enmienda dentro).
    text = plan_path.read_text(encoding="utf-8")
    absorbed = AMEND_LINE_RE.findall(text) if kind == "plan" else []
    if absorbed:
        plan_path.write_text(AMEND_LINE_RE.sub("", text), encoding="utf-8")
        for ca, ref in absorbed:
            print(f"Enmienda absorbida por re-validacion: {ca} ({ref}) — anotacion limpiada.")

    if not write_estado(plan_path, "VALIDADO"):
        return 1
    if aprobado and not write_aprobado(plan_path, aprobado):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
