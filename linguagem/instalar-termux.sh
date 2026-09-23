#!/usr/bin/env bash
set -e
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
mkdir -p "$PREFIX/bin"
cat > "$PREFIX/bin/hzhon" <<EOF
#!/data/data/com.termux/files/usr/bin/sh
exec python3 "$ROOT/hzhon_cli.py" "\$@"
EOF
chmod 755 "$PREFIX/bin/hzhon"
echo "Hzhon instalada em $PREFIX/bin/hzhon"
echo "Teste agora com: hzhon --help"
