#!/usr/bin/env python3
"""Validador estructural determinista del ecosistema SDD (ROADMAP 11.4a).

Caza los problemas MECANIZABLES que la auditoria experta encontro y que el
`wf-sdd-audit structural` por prosa no detecta (dio "CONSISTENTE" pese a
C1/C2/C6/C7 reales). Convierte esos hallazgos en guardas reproducibles para
blindar el saneamiento del Cajon A contra regresiones.

NO sustituye al agente `sdd-auditor`: produce los findings deterministas que el
agente funde en su reporte; el agente anade el juicio estructural NO mecanizable
encima (huerfanas con matiz, rootmap drift semantico, etc.).

Checks (cada finding: severidad, tipo, archivo:linea, mensaje):

  CITED-RULE-MISSING     [blocking]  Cita `Regla N de kb-X` pero N no existe en kb-X.
  CITED-SKILL-MISSING    [blocking]  Cita una kb-X que no existe como skill.
  CITED-RULE-ON-WORKFLOW [blocking]  Cita `Regla N de wf-X` (los wf tienen Pasos, no Reglas).
  ABSOLUTE-PATH          [blocking]  /Users/ o /home/ embebido en un .md del ecosistema.
  NAME-MISMATCH          [blocking]  name: del frontmatter != nombre de directorio (SKILL.md) / archivo (agente).
  REFERENCE-PATH-MISSING [blocking]  ruta a references/<f> citada en un SKILL.md que no resuelve en disco.
  SKILL-REF-MISSING      [warning]   Token `kb-X`/`wf-X` en docs que no es una skill real.
  ALLOWED-TOOLS-MISMATCH [blocking/warning] frontmatter allowed-tools no cubre el body.
  FORK-ASKUSER-CONFLICT  [blocking]  wf con context: fork que declara/usa AskUserQuestion (un fork no puede preguntar).
  DESCRIPTION-TOO-LONG   [warning]   description del frontmatter > 220 chars.
  USER-INVOCABLE-MISSING [warning]   wf sin user-invocable; kb sin user-invocable: false.

Uso:
    python3 sdd/scripts/sdd-structural-lint.py [--check] [--json]
                                               [--severity blocking|warning|all]
                                               [--root <path>]

Salida por defecto: reporte legible agrupado por severidad y tipo, con conteos.
  --check     exit 2 si hay >=1 blocking, 1 si solo warnings, 0 si limpio (CI).
  --json      lista estructurada de findings para consumo programatico.
  --severity  filtra los findings mostrados (default all).
  --root      raiz del arbol a escanear (default: el arbol del ecosistema en el
              que vive este script). Pensado para tests sobre fixtures aislados;
              el comportamiento por defecto es identico al de siempre.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SDD_ROOT = Path(__file__).resolve().parent.parent

# Directorios excluidos SIEMPRE del escaneo (mirror, vcs, artefactos de proyecto).
EXCLUDED_DIRS = {".claude", ".git", "__pycache__", "node_modules"}
# Nombres de directorio que delatan artefactos de proyecto consumidor (no ecosistema).
PROJECT_ARTIFACT_DIRS = {"features", ".sdd"}

DESC_MAX = 220

# --- Citas de regla en el cuerpo -------------------------------------------
# `Regla[s] N[, M y K] de `?kb-X`?`  (numeros separados por coma / y)
CITE_RULE_OF = re.compile(
    r"Reglas?\s+([\d,\s]+(?:y\s*\d+)?)\s+de\s+`?(kb-[\w-]+|wf-[\w-]+)`?",
    re.IGNORECASE,
)
# `` `?kb-X`? Regla[s] N ``  (skill antes, regla despues)
CITE_SKILL_RULE = re.compile(
    r"`?(kb-[\w-]+|wf-[\w-]+)`?\s+Reglas?\s+(\d+)",
)
# Heading de definicion de regla dentro de una KB.
RULE_HEADING = re.compile(r"^#{2,4}\s*Regla\s+(\d+)\s*:", re.MULTILINE)

# --- Paths absolutos --------------------------------------------------------
ABSOLUTE_PATH = re.compile(r"(/Users/|/home/)[^\s`)\]\"']*")

# --- Tokens de skill en docs ------------------------------------------------
SKILL_TOKEN = re.compile(r"`(kb-[\w-]+|wf-[\w-]+)`")
EXAMPLE_HINTS = ("ejemplo", "example", "p. ej.", "p.ej.", "<nombre>", "kb-<", "wf-<")

# --- Rutas a ficheros de references citadas en el cuerpo de un SKILL.md -----
# Solo marcamos formas que apuntan INEQUIVOCAMENTE a un fichero de references de
# una skill concreta, y resolvemos cada una contra la skill correcta:
#
#   ${CLAUDE_SKILL_DIR}/references/<f>   -> own references (forma canonica)
#   ./references/<f>                     -> own references (relativa explicita a si misma)
#   ../<otra-skill>/references/<f>       -> references de la skill hermana nombrada
#   <kb-X|wf-X>/references/<f>           -> references de la skill nombrada (cross-skill)
#
# NO marcamos `references/<f>` a secas (sin prefijo): es ambiguo en prosa
# (suele atribuirse a OTRA skill por el texto que lo rodea) y la forma canonica
# de auto-referencia es ${CLAUDE_SKILL_DIR} segun kb-sdd-creation-guide. Esto
# evita los falsos positivos de citas cruzadas y de ejemplos anti-patron.
REFERENCE_PATH_RE = re.compile(
    r"(?P<prefix>\$\{CLAUDE_SKILL_DIR\}/"          # own (canonica)
    r"|\.\./[\w.-]+/"                              # ../<otra-skill>/
    r"|\./"                                        # ./ (own explicita)
    r"|(?:kb-|wf-)[\w-]+/)"                        # <kb-X|wf-X>/ (cross-skill)
    r"references/(?P<rel>[\w./-]+\.\w+)"
)

# --- Frontmatter ------------------------------------------------------------
ALLOWED_TOOLS_RE = re.compile(r"^allowed-tools:\s*\[([^\]]*)\]", re.MULTILINE)
CONTEXT_FORK_RE = re.compile(r"^context:\s*fork\b", re.MULTILINE)
AGENT_RE = re.compile(r"^agent:\s*\S+", re.MULTILINE)
USER_INVOCABLE_RE = re.compile(r"^user-invocable:\s*(true|false)\b", re.MULTILINE)


class Finding:
    __slots__ = ("severity", "ftype", "path", "line", "message")

    def __init__(self, severity, ftype, path, line, message):
        self.severity = severity
        self.ftype = ftype
        self.path = path
        self.line = line
        self.message = message

    def as_dict(self):
        return {
            "severity": self.severity,
            "type": self.ftype,
            "file": self.path,
            "line": self.line,
            "message": self.message,
        }


def is_excluded(p: Path, also_docs: bool = False) -> bool:
    parts = set(p.relative_to(SDD_ROOT).parts)
    if parts & EXCLUDED_DIRS or parts & PROJECT_ARTIFACT_DIRS:
        return True
    if also_docs and "docs" in parts:
        return True
    return False


def iter_md(root: Path, exclude_docs: bool = False):
    """Todos los .md bajo root, excluyendo mirror/vcs/artefactos (y docs si se pide)."""
    for p in sorted(root.rglob("*.md")):
        if not is_excluded(p, also_docs=exclude_docs):
            yield p


def relpath(p: Path) -> str:
    return p.relative_to(SDD_ROOT).as_posix()


def split_frontmatter(text: str):
    """Devuelve (frontmatter_str, body_str, body_start_line) — body_start_line 1-based."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "", text, 1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = "".join(lines[1:i])
            body = "".join(lines[i + 1:])
            return fm, body, i + 2
    return "", text, 1


def frontmatter_value(fm: str, key: str):
    """Valor de una clave simple del frontmatter (solo la linea de la clave, sin continuaciones)."""
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", fm, re.MULTILINE)
    if not m:
        return None
    return m.group(1).strip()


# ---------------------------------------------------------------------------
# Indices del ecosistema
# ---------------------------------------------------------------------------

def build_skill_index():
    """Devuelve dos dicts:
       skills: {name: path}            (todas las skills kb-* y wf-*)
       rules:  {kb_name: set(int)}     (numeros de Regla definidos en cada kb)
    """
    skills = {}
    rules = {}
    for skill_md in SDD_ROOT.rglob("SKILL.md"):
        if is_excluded(skill_md):
            continue
        try:
            text = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, body, _ = split_frontmatter(text)
        name = frontmatter_value(fm, "name") or skill_md.parent.name
        skills[name] = skill_md
        if name.startswith("kb-"):
            nums = {int(n) for n in RULE_HEADING.findall(body)}
            rules[name] = nums
    return skills, rules


# ---------------------------------------------------------------------------
# Helpers de parseo de cuerpo (ignorar frontmatter description y code fences)
# ---------------------------------------------------------------------------

def line_iter_skip_codefences(text: str, skip_fences: bool):
    """Itera (lineno_1based, line) saltando lineas de frontmatter description y,
       opcionalmente, bloques ``` de codigo. Las lineas que empiezan por
       `description:` se saltan SIEMPRE (provenance historica intencionada)."""
    in_fence = False
    for idx, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if skip_fences and in_fence:
            continue
        if stripped.startswith("description:"):
            continue
        yield idx, line


def parse_rule_list(raw: str):
    """'4, 7 y 8' -> [4, 7, 8]. Robusto a separadores variados."""
    return [int(n) for n in re.findall(r"\d+", raw)]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_citations(skills, rules, findings):
    """CITED-RULE-MISSING / CITED-SKILL-MISSING / CITED-RULE-ON-WORKFLOW.

    Excluye docs/ (ROADMAP, FABLE_REPORT...): contienen el inventario historico
    de citas rotas como evidencia/fixtures — marcarlas seria ruido."""
    for md in iter_md(SDD_ROOT, exclude_docs=True):
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        rp = relpath(md)
        for lineno, line in line_iter_skip_codefences(text, skip_fences=True):
            # Patron A: "Regla[s] N[,M y K] de kb-X | wf-X"
            for m in CITE_RULE_OF.finditer(line):
                nums = parse_rule_list(m.group(1))
                target = m.group(2)
                _emit_citations(findings, rp, lineno, target, nums, skills, rules)
            # Patron B: "kb-X Regla[s] N"
            for m in CITE_SKILL_RULE.finditer(line):
                target = m.group(1)
                num = int(m.group(2))
                _emit_citations(findings, rp, lineno, target, [num], skills, rules)


def _emit_citations(findings, rp, lineno, target, nums, skills, rules):
    if target.startswith("wf-"):
        for n in nums:
            findings.append(Finding(
                "blocking", "CITED-RULE-ON-WORKFLOW", rp, lineno,
                f"Cita `Regla {n} de {target}`: los workflows tienen Pasos, no Reglas. "
                f"Reapunta a la kb-* que sea SSoT de esa regla."))
        return
    # target es kb-*
    if target not in skills:
        findings.append(Finding(
            "blocking", "CITED-SKILL-MISSING", rp, lineno,
            f"Cita `{target}` que no existe como skill en el ecosistema."))
        return
    kb_rules = rules.get(target, set())
    for n in nums:
        if n not in kb_rules:
            top = max(kb_rules) if kb_rules else 0
            findings.append(Finding(
                "blocking", "CITED-RULE-MISSING", rp, lineno,
                f"Cita `Regla {n} de {target}` pero esa KB no define la Regla {n} "
                f"(reglas existentes: {top and f'1..{top}' or 'ninguna'})."))


def check_absolute_paths(findings):
    """ABSOLUTE-PATH.

    Excluye docs/ (ROADMAP, FABLE_REPORT...): son reportes narrativos donde el
    path absoluto es CONTENIDO documental (evidencia de un hallazgo), no una
    referencia operativa que rompa en otra maquina. Los .md operativos del
    ecosistema (skills, agentes, README/DIAGRAMS/CLAUDE de fase) si se escanean."""
    for md in iter_md(SDD_ROOT, exclude_docs=True):
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        rp = relpath(md)
        for idx, line in enumerate(text.splitlines(), start=1):
            for m in ABSOLUTE_PATH.finditer(line):
                findings.append(Finding(
                    "blocking", "ABSOLUTE-PATH", rp, idx,
                    f"Path absoluto embebido: `{m.group(0)}`. Usa ${{CLAUDE_SKILL_DIR}} "
                    f"o una ruta relativa al repo."))


def check_skill_refs_in_docs(skills, findings):
    """SKILL-REF-MISSING — solo en README.md / DIAGRAMS.md / CLAUDE.md."""
    targets = ("README.md", "DIAGRAMS.md", "CLAUDE.md")
    for md in iter_md(SDD_ROOT):
        if md.name not in targets:
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        rp = relpath(md)
        in_fence = False
        for idx, line in enumerate(text.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            low = line.lower()
            if any(h in low for h in EXAMPLE_HINTS):
                continue
            for m in SKILL_TOKEN.finditer(line):
                token = m.group(1)
                if token not in skills:
                    findings.append(Finding(
                        "warning", "SKILL-REF-MISSING", rp, idx,
                        f"Referencia a `{token}` que no corresponde a ninguna skill instalada."))


def check_allowed_tools(findings):
    """ALLOWED-TOOLS-MISMATCH — solo en wf-*/SKILL.md."""
    for skill_md in sorted(SDD_ROOT.rglob("SKILL.md")):
        if is_excluded(skill_md):
            continue
        try:
            text = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, body, body_start = split_frontmatter(text)
        name = frontmatter_value(fm, "name") or skill_md.parent.name
        if not name.startswith("wf-"):
            continue
        rp = relpath(skill_md)

        at_m = ALLOWED_TOOLS_RE.search(fm)
        tools = set()
        if at_m:
            tools = {t.strip() for t in at_m.group(1).split(",") if t.strip()}
        has_fork = CONTEXT_FORK_RE.search(fm) is not None
        has_agent_decl = AGENT_RE.search(fm) is not None

        # --- Senal de Bash ---
        bash_line = _detect_bash(body, body_start)
        if bash_line and "Bash" not in tools:
            findings.append(Finding(
                "blocking", "ALLOWED-TOOLS-MISMATCH", rp, bash_line[0],
                f"El body usa shell ({bash_line[1]}) pero `Bash` no esta en allowed-tools "
                f"{sorted(tools)}."))

        # --- Senal de Write ---
        # Solo si el workflow NO tiene Bash: un wf con Bash escribe legitimamente via
        # script o redireccion (p. ej. wf-project-status/wf-release delegan la escritura
        # a sdd-*.py) y no necesita el tool Write. Esto evita el falso positivo de los
        # workflows mecanicos y de los que solo imprimen ("no genera ningun archivo").
        if "Bash" not in tools:
            write_line = _detect_write(body, body_start)
            if write_line and "Write" not in tools:
                findings.append(Finding(
                    "warning", "ALLOWED-TOOLS-MISMATCH", rp, write_line[0],
                    f"El workflow declara escribir un artefacto ({write_line[1]}) pero ni "
                    f"`Write` ni `Bash` estan en allowed-tools {sorted(tools)}."))

        # --- Senal de AskUserQuestion ---
        ask_line = _detect_token(body, body_start, "AskUserQuestion")
        if ask_line and "AskUserQuestion" not in tools:
            findings.append(Finding(
                "warning", "ALLOWED-TOOLS-MISMATCH", rp, ask_line[0],
                f"El body menciona usar `AskUserQuestion` pero no esta en allowed-tools "
                f"{sorted(tools)}."))

        # --- FORK-ASKUSER-CONFLICT (blocking) ---
        # AskUserQuestion NO esta disponible en subagentes ni forks (doc oficial de
        # Claude Code: las tools que dependen de la UI/estado del hilo principal se
        # excluyen "even when listed in the tools field"). Una wf-* con `context: fork`
        # que declare o use AskUserQuestion no puede presentar la pregunta: el fork
        # falla y el orquestador acaba improvisando la interaccion (no determinista).
        # Las skills interactivas corren en el hilo principal (sin fork) y delegan el
        # trabajo pesado via la tool `Agent`, que aisla su contexto igual de bien.
        if has_fork and ("AskUserQuestion" in tools or ask_line):
            findings.append(Finding(
                "blocking", "FORK-ASKUSER-CONFLICT", rp,
                ask_line[0] if ask_line else 1,
                "`context: fork` es incompatible con `AskUserQuestion`: un fork/subagente "
                "no puede presentar preguntas al usuario. Quita `context: fork` — la skill "
                "interactiva corre en el hilo principal y delega el trabajo pesado via `Agent`."))

        # --- Senal de Agent ---
        # Solo si hay invocacion explicita `Agent(` Y NO es patron fork.
        agent_call = _detect_agent_call(body, body_start)
        if agent_call and "Agent" not in tools and not (has_fork and has_agent_decl):
            findings.append(Finding(
                "warning", "ALLOWED-TOOLS-MISMATCH", rp, agent_call[0],
                f"El body invoca un subagente (`Agent(`) pero `Agent` no esta en "
                f"allowed-tools {sorted(tools)} y el frontmatter no es patron fork."))


def _detect_bash(body: str, body_start: int):
    """Devuelve (lineno, senal) de la primera senal de Bash, o None."""
    in_fence = False
    for off, line in enumerate(body.splitlines()):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        lineno = body_start + off
        if stripped.startswith("!"):
            return (lineno, "linea de comando `!`")
        # Senales de comando shell embebido en cualquier contexto.
        for sig in ("git ", "python3 ", "test -f", "rev-parse", "./gradlew", "find sdd"):
            if sig in line:
                return (lineno, f"comando `{sig.strip()}`")
    return None


def _detect_write(body: str, body_start: int):
    """Senal de que el workflow escribe un artefacto."""
    patterns = (
        r"\bEscrib[ei]\b.*\b(en|el|los|las|artefacto|archivo|reporte|fichero)\b",
        r"\bWrite\b",
        r"escribe el reporte",
        r"escribe.*\.md\b",
    )
    for off, line in enumerate(body.splitlines()):
        for pat in patterns:
            if re.search(pat, line, re.IGNORECASE):
                return (body_start + off, "menciona escribir salida")
    return None


def _detect_token(body: str, body_start: int, token: str):
    in_fence = False
    for off, line in enumerate(body.splitlines()):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if token in line:
            return (body_start + off, token)
    return None


def _detect_agent_call(body: str, body_start: int):
    for off, line in enumerate(body.splitlines()):
        if re.search(r"\bAgent\s*\(", line):
            return (body_start + off, "Agent(")
    return None


def check_frontmatter_fields(findings):
    """DESCRIPTION-TOO-LONG / USER-INVOCABLE-MISSING."""
    for skill_md in sorted(SDD_ROOT.rglob("SKILL.md")):
        if is_excluded(skill_md):
            continue
        try:
            text = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, _, _ = split_frontmatter(text)
        name = frontmatter_value(fm, "name") or skill_md.parent.name
        rp = relpath(skill_md)

        # description length (solo el valor de la clave, sin continuaciones)
        desc = frontmatter_value(fm, "description")
        if desc:
            value = desc.strip().strip('"').strip("'")
            if len(value) > DESC_MAX:
                findings.append(Finding(
                    "warning", "DESCRIPTION-TOO-LONG", rp, 1,
                    f"description de {len(value)} chars (> {DESC_MAX}). Recorta preservando el significado."))

        # user-invocable
        ui_m = USER_INVOCABLE_RE.search(fm)
        if name.startswith("wf-"):
            if ui_m is None:
                findings.append(Finding(
                    "warning", "USER-INVOCABLE-MISSING", rp, 1,
                    "wf-* sin campo `user-invocable:` en frontmatter (canon: `user-invocable: true`)."))
        elif name.startswith("kb-"):
            if ui_m is None or ui_m.group(1) != "false":
                findings.append(Finding(
                    "warning", "USER-INVOCABLE-MISSING", rp, 1,
                    "kb-* debe declarar `user-invocable: false` (no se enruta; se inyecta en agentes)."))


def check_name_mismatch(findings):
    """NAME-MISMATCH — el name: del frontmatter debe coincidir con:
       - el nombre del directorio padre, para */SKILL.md
       - el basename sin extension, para */agents/<x>.md
    """
    # SKILL.md: name == nombre del directorio que lo contiene.
    for skill_md in sorted(SDD_ROOT.rglob("SKILL.md")):
        if is_excluded(skill_md):
            continue
        try:
            text = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, _, _ = split_frontmatter(text)
        name = frontmatter_value(fm, "name")
        if name is None:
            continue
        name = name.strip().strip('"').strip("'")
        dirname = skill_md.parent.name
        if name != dirname:
            findings.append(Finding(
                "blocking", "NAME-MISMATCH", relpath(skill_md), 1,
                f"`name: {name}` no coincide con el directorio padre `{dirname}`. "
                f"El name de un SKILL.md debe ser el nombre de su directorio."))

    # Agentes: name == basename sin extension del archivo .md en */agents/.
    for agent_md in sorted(SDD_ROOT.rglob("*.md")):
        if is_excluded(agent_md):
            continue
        if "agents" not in agent_md.relative_to(SDD_ROOT).parts:
            continue
        try:
            text = agent_md.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, _, _ = split_frontmatter(text)
        name = frontmatter_value(fm, "name")
        if name is None:
            continue
        name = name.strip().strip('"').strip("'")
        stem = agent_md.stem
        if name != stem:
            findings.append(Finding(
                "blocking", "NAME-MISMATCH", relpath(agent_md), 1,
                f"`name: {name}` no coincide con el nombre de archivo `{stem}`. "
                f"El name de un agente debe ser el basename del .md sin extension."))


def check_reference_paths(findings):
    """REFERENCE-PATH-MISSING — toda ruta a references/<f> citada en un SKILL.md
       que no resuelve en disco. Resuelve relativo al directorio del SKILL.md.

       Ignora bloques de codigo de ejemplo para no marcar plantillas/placeholders,
       y descarta paths con placeholders (`<...>`, `${...}` que no sea
       CLAUDE_SKILL_DIR) que no apuntan a un fichero concreto."""
    for skill_md in sorted(SDD_ROOT.rglob("SKILL.md")):
        if is_excluded(skill_md):
            continue
        try:
            text = skill_md.read_text(encoding="utf-8")
        except OSError:
            continue
        rp = relpath(skill_md)
        skill_dir = skill_md.parent
        skills_root = skill_dir.parent  # el directorio `skills/` que contiene las skills hermanas
        for lineno, line in line_iter_skip_codefences(text, skip_fences=True):
            for m in REFERENCE_PATH_RE.finditer(line):
                prefix = m.group("prefix")
                rel = m.group("rel")
                # Descarta placeholders no resolubles (no son una ruta concreta).
                if "<" in rel or ">" in rel or "<" in prefix or ">" in prefix:
                    continue
                if prefix.startswith("${CLAUDE_SKILL_DIR}") or prefix == "./":
                    target = (skill_dir / "references" / rel).resolve()
                elif prefix.startswith("../"):
                    # ../<otra-skill>/  -> hermana en el mismo directorio skills/
                    sibling = prefix[len("../"):].rstrip("/")
                    target = (skills_root / sibling / "references" / rel).resolve()
                else:
                    # <kb-X|wf-X>/  -> skill nombrada. Puede ser hermana directa o
                    # vivir en otro nivel (plan/, tasks/); buscamos su directorio real.
                    named = prefix.rstrip("/")
                    sib = skills_root / named
                    if not sib.is_dir():
                        matches = [d.parent for d in SDD_ROOT.rglob(f"{named}/SKILL.md")
                                   if not is_excluded(d)]
                        if matches:
                            sib = matches[0]
                    target = (sib / "references" / rel).resolve()
                if not target.exists():
                    citation = f"{prefix}references/{rel}"
                    findings.append(Finding(
                        "blocking", "REFERENCE-PATH-MISSING", rp, lineno,
                        f"Referencia a `{citation}` que no resuelve en disco "
                        f"(esperado: {relpath(target) if str(target).startswith(str(SDD_ROOT)) else target})."))


# ---------------------------------------------------------------------------
# Reporte
# ---------------------------------------------------------------------------

def run_all():
    skills, rules = build_skill_index()
    findings = []
    check_citations(skills, rules, findings)
    check_absolute_paths(findings)
    check_skill_refs_in_docs(skills, findings)
    check_allowed_tools(findings)
    check_frontmatter_fields(findings)
    check_name_mismatch(findings)
    check_reference_paths(findings)
    # Orden estable: severidad (blocking primero), tipo, path, linea.
    sev_order = {"blocking": 0, "warning": 1}
    findings.sort(key=lambda f: (sev_order.get(f.severity, 9), f.ftype, f.path, f.line))
    return findings


def filter_severity(findings, severity):
    if severity == "all":
        return findings
    return [f for f in findings if f.severity == severity]


def render_report(findings, total_findings):
    lines = ["=== sdd-structural-lint — validador estructural determinista del ecosistema SDD ==="]
    if not findings:
        lines.append("Sin findings en el filtro seleccionado.")
    blocking = [f for f in findings if f.severity == "blocking"]
    warning = [f for f in findings if f.severity == "warning"]

    for sev, group in (("BLOCKING", blocking), ("WARNING", warning)):
        if not group:
            continue
        lines.append("")
        lines.append(f"--- {sev} ({len(group)}) ---")
        by_type = {}
        for f in group:
            by_type.setdefault(f.ftype, []).append(f)
        for ftype in sorted(by_type):
            items = by_type[ftype]
            lines.append(f"  [{ftype}] ({len(items)})")
            for f in items:
                lines.append(f"    {f.path}:{f.line}  {f.message}")

    # Conteo agregado por tipo
    lines.append("")
    lines.append("--- Conteo por tipo ---")
    counts = {}
    for f in total_findings:
        counts[(f.severity, f.ftype)] = counts.get((f.severity, f.ftype), 0) + 1
    for (sev, ftype), n in sorted(counts.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        lines.append(f"  {sev:8} {ftype:24} {n}")
    n_block = sum(1 for f in total_findings if f.severity == "blocking")
    n_warn = sum(1 for f in total_findings if f.severity == "warning")
    lines.append("")
    lines.append(f"TOTAL: {n_block} blocking, {n_warn} warning")
    return "\n".join(lines)


def main() -> int:
    global SDD_ROOT
    args = sys.argv[1:]
    as_json = "--json" in args
    check_mode = "--check" in args
    severity = "all"
    if "--severity" in args:
        i = args.index("--severity")
        if i + 1 < len(args) and args[i + 1] in ("blocking", "warning", "all"):
            severity = args[i + 1]
        else:
            print("ERROR: --severity requiere blocking|warning|all", file=sys.stderr)
            return 1
    if "--root" in args:
        i = args.index("--root")
        if i + 1 >= len(args):
            print("ERROR: --root requiere una ruta", file=sys.stderr)
            return 1
        root = Path(args[i + 1]).resolve()
        if not root.is_dir():
            print(f"ERROR: --root no es un directorio: {root}", file=sys.stderr)
            return 1
        SDD_ROOT = root

    findings = run_all()
    shown = filter_severity(findings, severity)

    if as_json:
        print(json.dumps([f.as_dict() for f in shown], ensure_ascii=False, indent=2))
    else:
        print(render_report(shown, findings))

    if check_mode:
        if any(f.severity == "blocking" for f in findings):
            return 2
        if any(f.severity == "warning" for f in findings):
            return 1
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
