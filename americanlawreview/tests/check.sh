set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

pdftotext "$ROOT/build/demo.pdf" "$ROOT/build/demo.txt"
pdftotext "$ROOT/build/final-demo.pdf" "$ROOT/build/final-demo.txt"
pdftotext "$ROOT/build/package-demo.pdf" "$ROOT/build/package-demo.txt"

while IFS= read -r line; do
  case "$line" in
    ''|\#*) continue ;;
  esac
  file=${line%%::*}
  snippet=${line#*::}
  if ! grep -F "$snippet" "$ROOT/build/$file" >/dev/null; then
    echo "Missing expected snippet in $file: $snippet" >&2
    exit 1
  fi
done < "$ROOT/tests/expected-snippets.txt"

echo "americanlawreview checks passed"
