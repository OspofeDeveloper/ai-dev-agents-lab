#!/bin/bash
# install.sh — Distribuye los templates compartidos a las skills que los necesitan.
# Ejecutar desde el directorio sdd/: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_DIR="$SCRIPT_DIR/shared/templates"

copy_template() {
  local filename="$1"
  local dest_dir="$2"
  local src="$SHARED_DIR/$filename"
  local dst="$dest_dir/$filename"

  if [ ! -f "$src" ]; then
    echo "ERROR: Template no encontrado: $src"
    exit 1
  fi

  mkdir -p "$dest_dir"
  cp "$src" "$dst"
  echo "  ✓ $dst"
}

echo "Instalando templates SDD compartidos..."
echo ""

echo "→ spec-decompose"
copy_template "feature_spec_template.md"  "$SCRIPT_DIR/spec/skills/spec-decompose/references"
copy_template "feature_readme_template.md" "$SCRIPT_DIR/spec/skills/spec-decompose/references"

echo "→ spec-fast-track"
copy_template "feature_spec_template.md"  "$SCRIPT_DIR/spec/skills/spec-fast-track/references"
copy_template "feature_readme_template.md" "$SCRIPT_DIR/spec/skills/spec-fast-track/references"

echo ""
echo "Done. Templates distribuidos correctamente."
