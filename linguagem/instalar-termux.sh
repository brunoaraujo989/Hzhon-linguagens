#!/usr/bin/env bash
set -euo pipefail

# Instalador POSIX para Termux, Linux, macOS e ambientes Unix semelhantes.
# Não exige pacotes externos: Python 3 é a única dependência do runtime.
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
else
    echo "Hzhon precisa do Python 3. Instale-o pelo gerenciador do seu sistema e tente novamente." >&2
    exit 1
fi

if ! "$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "Hzhon precisa do Python 3.10 ou mais recente." >&2
    exit 1
fi

if [ -n "${PREFIX:-}" ] && [ -d "$PREFIX" ] && [ -w "$PREFIX" ]; then
    DEST="$PREFIX/bin"
elif [ -n "${HOME:-}" ] && { [ -d "$HOME/.local/bin" ] || mkdir -p "$HOME/.local/bin"; }; then
    DEST="$HOME/.local/bin"
else
    echo "Não encontrei uma pasta executável para instalar o comando hzhon." >&2
    exit 1
fi

mkdir -p "$DEST"
cat > "$DEST/hzhon" <<EOF
#!/usr/bin/env sh
exec "$PYTHON" "$ROOT/hzhon_cli.py" "\$@"
EOF
chmod 755 "$DEST/hzhon"

echo "Hzhon instalada em $DEST/hzhon"
if ! command -v hzhon >/dev/null 2>&1; then
    echo "Se o comando ainda não for encontrado, adicione esta pasta ao PATH:"
    echo "  export PATH=\"$DEST:\$PATH\""
fi
echo "Teste agora com: hzhon --help"