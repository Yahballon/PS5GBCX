#!/usr/bin/env bash
# (AI-assisted) Hosted PS5GBC native dependency preparation.
# All files stay in ignored working directories; no ROM/BIOS is downloaded.
set -euo pipefail

repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
export PS5GBC_DEPS="${PS5GBC_DEPS:-$repo/.cache/ps5-build}"
mkdir -p "$PS5GBC_DEPS"

# Use the independently working PS5MesenX Vulkan driver + SDK bootstrap.
bash "$repo/gbc/tools/bootstrap_native.sh"

# Verified PacBrew v0.40.2 archive: libcurl, libpsl, libssl, libcrypto,
# libzstd and libz for the existing NFS/HTTP-enabled frontend.
bash "$repo/gbc/tools/setup-pacbrew-dependencies.sh" --all
export LIBZ_PREFIX="$repo/gbc/.deps/pacbrew/v0.40.2/sysroot/user/homebrew"
for name in curl psl ssl crypto zstd z; do
  test -s "$LIBZ_PREFIX/lib/lib$name.a" || { echo "Missing PacBrew lib$name.a" >&2; exit 1; }
done
test -s "$LIBZ_PREFIX/include/zlib.h"

sdk="$PS5GBC_DEPS/PS5_Vulkan/.deps/native/ps5-payload-sdk"
test -x "$sdk/bin/prospero-clang"
toolchain="$sdk/toolchain/prospero.cmake"
test -f "$toolchain" || { echo "SDK CMake toolchain unavailable: $toolchain" >&2; exit 1; }

# Exact public libnfs 5.0.3 (NFSv3). Compile for PS5, not the host.
nfs_src="$PS5GBC_DEPS/libnfs"
if [[ ! -d "$nfs_src/.git" ]]; then
  git clone -q https://github.com/sahlberg/libnfs.git "$nfs_src"
fi
git -C "$nfs_src" checkout -q --detach libnfs-5.0.3
out="$PS5GBC_DEPS/libnfs-output"
bash "$repo/ps5/tools/build-libnfs.sh" "$nfs_src" "$out" "$toolchain"
ln -sfn "$out/install" "$PS5GBC_DEPS/libnfs-install"
test -s "$PS5GBC_DEPS/libnfs-install/lib/libnfs.a"
test -s "$PS5GBC_DEPS/libnfs/COPYING"

# The title-bound helper is generated from pinned public Lapy source by
# gbc/tools/build-lapy-helper.py during the native title build.
printf 'PS5GBC_DEPS=%s\nLIBZ_PREFIX=%s\n' "$PS5GBC_DEPS" "$LIBZ_PREFIX"
echo "Ready: native PS5 Vulkan, SDK, PacBrew and libnfs (AI-assisted)"
