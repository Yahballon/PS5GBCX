#!/usr/bin/env python3
"""(AI-assisted) Fail release build if PS5 installer package is incomplete."""
from pathlib import Path
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parents[2]
meta = json.loads((root / "app.json").read_text())
assert meta["titleId"] == "PPSA99210", "wrong title ID"
package = root / "gbc" / "build-shelf" / (
    f'GBCXY-v{meta["version"]}-by-YAHBALLON.zip'
)
if not package.is_file():
    raise FileNotFoundError(f"Signed GBCXY installer not found: {package}")
required = {
    "PPSA99210/eboot.bin",
    "PPSA99210/sce_sys/param.json",
    "PPSA99210/sce_sys/icon0.png",
    "PPSA99210/sce_module/libc.prx",
    "PPSA99210/lapy.elf",
    "PPSA99210/lapy-manifest.json",
    "PPSA99210/build-manifest.json",
}
with zipfile.ZipFile(package) as z:
    bad = z.testzip()
    assert bad is None, f"Bad ZIP entry: {bad}"
    names = set(z.namelist())
    assert required <= names, f"Missing installer files: {sorted(required - names)}"
    assert any(x.startswith("PPSA99210/licenses/") for x in names)
    param = json.loads(z.read("PPSA99210/sce_sys/param.json"))
    assert param["titleId"] == "PPSA99210"
    manifest = json.loads(z.read("PPSA99210/build-manifest.json"))
    assert manifest["title"] == "PPSA99210"
    for name, expected in manifest["files"].items():
        actual = hashlib.sha256(z.read("PPSA99210/" + name)).hexdigest()
        assert actual == expected, f"SHA mismatch: {name}"
print("PASS (AI-assisted): signed native app package layout, ZIP CRC, metadata and manifest file hashes")
