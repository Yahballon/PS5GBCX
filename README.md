<div align="center">

# GBCXY

### 8-Bit Colors. Next-Gen CoverFlow.

**v2.0.0 · by YAHBALLON · PPSA99210**

[![Native PS5 Build](https://github.com/Yahballon/PS5GBCX/actions/workflows/build-gbcxy.yml/badge.svg)](https://github.com/Yahballon/PS5GBCX/actions/workflows/build-gbcxy.yml)
[![GitHub releases](https://img.shields.io/github/v/release/Yahballon/PS5GBCX?style=flat-square)](https://github.com/Yahballon/PS5GBCX/releases)

</div>

**GBCXY** is a PlayStation 5 homebrew emulator for **Game Boy and Game Boy Color**, powered by the mGBA 0.10.5 GB/GBC core and a 3D Vulkan CoverFlow frontend. It builds on the same modern frontend foundation as GBAXY, with five original themes and its own animated loading sequence.

> **Compatibility:** the repository remains `PS5GBCX`, Title ID remains **`PPSA99210`**, and existing games, settings, cached box art and saves remain in **`/data/PS5GBC/`**. This is an in-place upgrade, not a new app title.

## Highlights

| Feature | Description |
| --- | --- |
| **3D CoverFlow** | Animated glass cartridge cases, neon edges, cover reflections and wraparound browsing |
| **Auto cover art** | GB and GBC use their **separate** Libretro Named_Boxarts libraries, with region/name fallbacks and a local disk cache |
| **Five new themes** | Chromatic Shift, Pocket Forest, Berry Soda, Polar LCD and Retro Amber |
| **Chromatic Pocket** | Original animated 8-bit boot: rotating color-pixel mosaic, LCD scanlines, cartridge emblem and genuine ROM scan counts |
| **Native GB/GBC emulation** | mGBA 0.10.5 with GB/GBC core enabled; preserves ROM scanning, audio, saves and controller mappings |
| **Flexible scaling** | Stretch to full screen, original GB/GBC aspect ratio or integer scaling |
| **Safe PS5 exit** | In the library, Circle opens the close confirmation, Cross confirms, Circle cancels. Shutdown uses `sceSystemServiceLoadExec("exit", nullptr)` rather than unsupported libc `exit(0)`. |

### Choose your theme

- **Chromatic Shift** — multicolor turquoise and purple; default
- **Pocket Forest** — LCD greens and spring-leaf highlights
- **Berry Soda** — pink, raspberry and sunset orange
- **Polar LCD** — icy blue and white glass
- **Retro Amber** — dark gold inspired by vintage handheld screens

Select a theme under **Settings → Appearance → Theme**. The selection is stored in the existing global configuration.

## Box art sources

GBCXY uses the existing local cover folder and cache first. For missing covers it looks up No-Intro names and common USA, Europe and Japan region variants in the correct system-specific directories:

- **Game Boy (.gb):** [Libretro GB Named_Boxarts](https://thumbnails.libretro.com/Nintendo%20-%20Game%20Boy/Named_Boxarts/)
- **Game Boy Color (.gbc):** [Libretro GBC Named_Boxarts](https://thumbnails.libretro.com/Nintendo%20-%20Game%20Boy%20Color/Named_Boxarts/)

Game Boy artwork will not be incorrectly selected from the Game Boy Color library (or the reverse). Portrait art stays portrait, landscape artwork keeps its complete source image, and reflections follow the same geometry. Cover downloads happen on demand and are cached for the next boot.

## Installation / updating

1. Download the latest compiled **`PPSA99210.zip`** from [Releases](https://github.com/Yahballon/PS5GBCX/releases). A GitHub source-code ZIP is **not** an installable PS5 build.
2. Extract the **complete `PPSA99210` folder**, retaining `eboot.bin`, `sce_sys`, `sce_module` and the packaged helper.
3. Copy it to a supported PS5 homebrew install folder, commonly `/data/homebrew/PPSA99210/`, and start **GBCXY** from your jailbroken PS5.

### Game folders and saved data

```text
/data/PS5GBC/games/
/data/PS5GBC/roms/
/data/PS5GBC/saves/
/data/PS5GBC/states/
/data/PS5GBC/covers/
/data/PS5GBC/cache/
/data/PS5GBC/logs/
```

You can also scan USB game directories such as `/mnt/usb0/homebrew/PS5GBC/games/` and configured NFS shares. Use your own legally acquired GB/GBC game files; the repository includes **no ROMs**.

## Source layout and builds

The [**GBCXY Native Build & Release**](.github/workflows/build-gbcxy.yml) workflow performs automated source/box-art/controller regression tests and compiles a genuine native signed PS5 package from source. Main-branch builds publish a release tagged `v2.0.0`; version metadata is maintained in `app.json` and `gbc/src/gbcxy_build_version.h`.

```text
gbc/src/                   GB/GBC core wrapper, emulator and Chromatic Pocket animation
gbc/third_party/mgba/      Original open-source mGBA source
gbc/tools/                 Native PS5 build scripts and regression checks
ps5/frontend/              Game library, cover worker, settings, native Vulkan bridge
ps5/porpoise_original/     Licensed Porpoise 3D UI code
ps5/frontend/assets/       GBCXY icon and embedded UI assets
tests/                     GBCXY visual, cover-provider and exit regression tests
.github/workflows/         Automated signed build and release
```

GBCXY builds require the PS5 payload toolchain, native Vulkan dependencies and compatible Linux SDK tools. Host-only builds cannot produce an installable PS5 binary.

## Credits and licensing

**GBCXY by YAHBALLON.** GB/GBC emulation is provided by [mGBA](https://github.com/mgba-emu/mgba), with a frontend adapted from [Porpoise](https://github.com/elripalda/Porpoise-Dolphin-Emulator-for-PS5) and open-source PS5 development frameworks. Preserve and consult bundled third-party licenses and notices.

This independent community homebrew project is not affiliated with Sony or Nintendo. It does not distribute commercial ROMs, copyrighted BIOS files or pirated games. Console testing is needed before release builds should be considered fully verified.
