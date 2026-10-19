"""(AI-assisted) Check publishable source and an optional PS5GBC release ZIP."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def check_source():
    # The release is assembled from committed source only. Generated SDK
    # tarballs, compiled objects and downloaded dependencies are untracked:
    # checking them here would cause false 100-MB source-limit failures.
    result = subprocess.run(
        ['git', 'ls-files', '--cached', '-z'],
        cwd=ROOT, check=True, capture_output=True,
    )
    errors = []
    paths = set(result.stdout.decode('utf-8').split('\0')) - {''}
    for name in sorted(paths):
        path = ROOT / name
        if not path.is_file():
            continue
        if path.stat().st_size >= 100 * 1024 * 1024:
            errors.append(f'File exceeds GitHub source size limit: {name}')
        if path.suffix.lower() in {'.gb', '.gbc', '.gba', '.sav', '.rtc', '.elf', '.prx', '.pkg'}:
            errors.append(f'Runtime/game file in publishable source: {name}')
    metadata = json.loads((ROOT / 'gbc/sce_sys/param.json').read_text())
    if metadata.get('titleId') != 'PPSA99210':
        errors.append('Incorrect app title ID')
    if json.loads((ROOT / 'sce_sys/param.json').read_text()) != metadata:
        errors.append('Root and packaged app metadata differ')
    for name in ['README.md', 'BUILDING.md', 'INSTALL.md', 'TESTING.md',
                 'LICENSE', 'COPYING.GPLv3', 'THIRD_PARTY_NOTICES.md',
                 'gbc/third_party/mgba/LICENSE']:
        if name not in paths:
            errors.append(f'Missing publishable documentation/license: {name}')
    print(f'Checked {len(paths)} publishable source files.')
    return errors


def check_package(path):
    errors = []
    prefix = 'PPSA99210/'
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            errors.append('Duplicate ZIP entries')
        for name in names:
            parts = PurePosixPath(name)
            if parts.is_absolute() or '..' in parts.parts or '\\' in name or ':' in name:
                errors.append(f'Unsafe ZIP path: {name}')
        if archive.testzip():
            errors.append('ZIP CRC check failed')
        required = ['eboot.bin', 'sce_module/libc.prx', 'sce_sys/param.json',
                    'sce_sys/icon0.png', 'lapy.elf', 'lapy-manifest.json',
                    'build-manifest.json', 'licenses/GPLv3.txt', 'licenses/mGBA-MPL-2.0.txt']
        for name in required:
            if prefix + name not in names:
                errors.append(f'Missing package file: {name}')
        if prefix + 'build-manifest.json' in names:
            manifest = json.loads(archive.read(prefix + 'build-manifest.json'))
            for name, digest in manifest['files'].items():
                full = prefix + name
                if full not in names or hashlib.sha256(archive.read(full)).hexdigest() != digest:
                    errors.append(f'Manifest mismatch: {name}')
            payload = {n[len(prefix):] for n in names if n.startswith(prefix)
                       and not n.endswith('/') and n != prefix + 'build-manifest.json'}
            if payload != set(manifest['files']):
                errors.append('Manifest does not cover all package files')
        if prefix + 'sce_sys/param.json' in names:
            if json.loads(archive.read(prefix + 'sce_sys/param.json')) != json.loads(
                    (ROOT / 'gbc/sce_sys/param.json').read_text()):
                errors.append('Package metadata differs from source')
    print(f'SHA-256: {hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, help='Also verify a built release ZIP')
    args = parser.parse_args()
    errors = check_source()
    if args.package:
        errors.extend(check_package(args.package))
    for error in errors:
        print(f'FAIL: {error}')
    if not errors:
        print('PASS: release file checks (console validation remains separate).')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
