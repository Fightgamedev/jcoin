#!/bin/sh
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE"
python3 - <<'PY'
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

with ZipFile("JCoin-Wallet-client.zip", "w", ZIP_DEFLATED) as bundle:
    bundle.write("JCoin-Wallet.html")
    bundle.write("docs/BROWSER-CLIENT-README.md", "README.md")
PY
printf '%s\n' "Built $HERE/JCoin-Wallet-client.zip"
