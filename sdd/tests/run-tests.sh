#!/usr/bin/env bash
# Runner de la suite de tests de los scripts deterministas de sdd/scripts/.
# Solo stdlib (unittest); cero dependencias externas. Corre desde la raiz del repo.
set -euo pipefail

# Raiz del repo = dos niveles por encima de este script (sdd/tests/ -> repo/).
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

exec python3 -m unittest discover -s sdd/tests -p 'test_*.py' -v
