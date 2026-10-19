#!/usr/bin/env python3
"""Static GB/GBC port guard: avoid wrong boxart or SIGSYS process shutdown."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
app=json.loads((root/'app.json').read_text())
assert app['titleId']=='PPSA99210' and app['version']=='2.0.0'
front=(root/'ps5/frontend/fe_exact_porpoise.cpp').read_text()
opts=(root/'ps5/frontend/fe_options.cpp').read_text()
for theme in ('chromatic-shift','pocket-forest','berry-soda','polar-lcd','retro-amber'):
    assert theme in front and theme in opts,theme
assert 'GBCXY' in front and 'gbcxy_build::kVersion' in front
urls=(root/'gbc/src/cover_urls.h').read_text()
assert '"Nintendo%20-%20Game%20Boy"' in urls
assert '"Nintendo%20-%20Game%20Boy%20Color"' in urls
assert '"/Named_Boxarts/"' in urls
assert 'path.ends_with(".gb")' in urls and 'path.ends_with(".gbc")' in urls
assert 'system!=std::string(e.system)' in urls
frame=(root/'gbc/src/shelf_runtime.cpp').read_text()
assert 'mgba_gb_model' in frame and 'renderer.UpdateTexture(' not in frame
ps5=(root/'ps5/frontend/fe_ps5.cpp').read_text()
main=(root/'gbc/src/main_shelf.cpp').read_text()
assert 'gbcxy_exit_to_shell(' in ps5 and 'sceSystemServiceLoadExec("exit",nullptr)' in main
assert '::exit(0)' not in ps5 and 'return 0;' not in main
assert (root/'ps5/porpoise_original/src/ui_gfx.cpp').is_file()
assert 'CHROMATIC POCKET' in (root/'gbc/src/loading.cpp').read_text()
for helper in ('build_generated_psbc.py','build_agc_imports.py'):
    helper_text=(root/'gbc/tools'/helper).read_text()
    assert '"gba/build-shelf' not in helper_text,helper
    assert '"gbc/build-shelf' in helper_text,helper
hygiene=(root/'gbc/tools/check_release.py').read_text()
assert "['git', 'ls-files', '--cached', '-z']" in hygiene
assert "'--others'" not in hygiene
verify=(root/'gbc/tools/verify_package.py').read_text()
assert 'root / "gba/build-shelf' not in verify
assert 'root / "gbc" / "build-shelf"' in verify
assert 'meta["version"]' in verify
print("PASS: GBCXY themes, correct GB/GBC covers, GB core, SDK archives and native exit")
