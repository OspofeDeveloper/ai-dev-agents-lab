#!/usr/bin/env python3
"""Merge del settings.json del ecosistema SDD sobre el settings.json del proyecto.

Uso: merge-claude-settings.py <source_settings.json> <dest_settings.json>

- Si dest no existe -> copia source tal cual.
- Si dest existe -> merge conservador, sin destruir nada del proyecto:
    * hooks: por cada evento del source, anade cada entrada cuyo "matcher" no
      este ya registrado en el dest para ese evento. Las entradas existentes
      del proyecto se preservan intactas.
    * resto de claves de primer nivel del source: solo se anaden si no existen
      en el dest (el valor del proyecto siempre gana).
- Idempotente: re-ejecutar no duplica entradas.
- Migracion: elimina del dest los hooks SDD obsoletos (identificados por su
  comando EXACTO en DEPRECATED_HOOK_COMMANDS) antes de mergear, para que la
  entrada que los sustituye pueda entrar. Nunca toca hooks ajenos al SDD.

Compartido por sdd/install.sh y tech/<stack>/install.sh (SSoT del merge).
"""
import json
import sys

# Comandos de hooks SDD de versiones anteriores, sustituidos por otra entrada.
# Solo se eliminan por coincidencia EXACTA del comando (jamas por matcher).
DEPRECATED_HOOK_COMMANDS = {
    # <=0.1.0: auto-allow universal de Skills — sustituido por sdd-skill-allow.py
    # (solo aprueba wf-*; ROADMAP 1.4)
    'echo \'{"hookSpecificOutput": {"hookEventName": "PermissionRequest", "decision": {"behavior": "allow"}}}\'',
}


def drop_deprecated(dest) -> bool:
    """Elimina hooks obsoletos del dest. Devuelve True si cambio algo."""
    changed = False
    for event, entries in (dest.get("hooks") or {}).items():
        for entry in list(entries):
            hooks = entry.get("hooks") or []
            kept = [h for h in hooks if h.get("command") not in DEPRECATED_HOOK_COMMANDS]
            if len(kept) != len(hooks):
                changed = True
                if kept:
                    entry["hooks"] = kept
                else:
                    entries.remove(entry)
    return changed


def main() -> int:
    if len(sys.argv) != 3:
        print("Uso: merge-claude-settings.py <source.json> <dest.json>", file=sys.stderr)
        return 1

    src_path, dest_path = sys.argv[1], sys.argv[2]

    with open(src_path) as f:
        src = json.load(f)

    try:
        with open(dest_path) as f:
            dest = json.load(f)
    except FileNotFoundError:
        dest = None

    if dest is None:
        with open(dest_path, "w") as f:
            json.dump(src, f, indent=2)
            f.write("\n")
        print(f"settings.json creado en {dest_path}")
        return 0

    changed = drop_deprecated(dest)

    # Merge de hooks: anadir matchers del source ausentes en el dest
    for event, src_entries in src.get("hooks", {}).items():
        dest_entries = dest.setdefault("hooks", {}).setdefault(event, [])
        existing_matchers = {e.get("matcher") for e in dest_entries}
        for entry in src_entries:
            if entry.get("matcher") not in existing_matchers:
                dest_entries.append(entry)
                changed = True

    # Resto de claves de primer nivel: solo si no existen en el dest
    for key, value in src.items():
        if key != "hooks" and key not in dest:
            dest[key] = value
            changed = True

    if changed:
        with open(dest_path, "w") as f:
            json.dump(dest, f, indent=2)
            f.write("\n")
        print(f"settings.json mergeado en {dest_path} (contenido previo preservado)")
    else:
        print(f"settings.json ya al dia en {dest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
