## PS5GBC is a passion project, not a piracy project.
<p align="center">
  <img src="screenshots/background.png" alt="PS5NES game shelf">
</p>

**Game Boy and Game Boy Color Emulator on your PS5, with the original PS5SX2 cover-flow interface.**

**v1 — by YAHBALLON** · **App ID: PPSA99210**

A GB/GBC-only port based on PS5GBA and mGBA 0.10.5. The GBA core is disabled in this build.

## Features

- `.gb` and `.gbc` ROMs only; ZIP containers may contain exactly one GB/GBC ROM. `.gba` files are rejected.
- Native 160×144 video, approximately 59.7275 FPS, and stereo output resampled to 48 kHz.
- Local, USB and NFS loading; cached library, rescan/reset and recent-first ordering.
- Native Vulkan output up to 4K, ORIGINAL / HD SMOOTH / ENHANCED presets, scaling and color settings.
- Separate SRAM, RTC battery data and one save-state slot per ROM.
- Configurable DualSense buttons, state/menu shortcuts and fast forward.
- Yellow handheld logo and GB/GBC Libretro covers with R2 refresh.

## Install and games

Download the app ZIP from [GitHub Releases](https://github.com/Yahballon/PS5GBC/releases) when available. GitHub's source archives contain source code and must be built first. Extract the **PPSA99210** folder into `/data/homebrew/` or your usual compatible homebrew launcher location. Keep `eboot.bin`, `sce_module/libc.prx`, `sce_sys/`, `lapy.elf` and `lapy-manifest.json` together.

~~~text
/data/PS5GBC/games/
/data/PS5GBC/roms/
/data/homebrew/PS5GBC/games/
/data/homebrew/PPSA99210/games/
/mnt/usb0/homebrew/PS5GBC/games/
/mnt/usb0/homebrew/PS5GBC/roms/
~~~

USB0–7 and recursive subfolders are supported. Configure an NFS share in All games settings, for example `nfs://192.168.1.10/GBC`, then restart. ZIPs must contain one `.gb` or `.gbc`; multi-ROM, encrypted and ZIP64 archives are unsupported.

Persistent files live under `/data/PS5GBC/`: battery data in `saves/*.sav` and `saves/*.rtc`, states in `states/`, settings in `gs.ini` and `settings/`, covers/cache in their own folders, and startup output in `logs/boot.log`. Fallback: `/download0/PS5GBC/`. Keep this data when replacing app files.

## Controls

| DualSense | GB/GBC |
| --- | --- |
| Cross / Circle | A / B |
| D-pad | Directions |
| Options / Create | Start / Select |
| Touchpad click | Return to library |
| L2 held | Fast forward, muted audio |
| L3 + R3 + Up / Down | Save / load state |

Square opens settings on the shelf. L1/R1 selects This game / All games; L2/R2 switches Settings / Controls. Button assignments are configurable. R2 on the shelf refreshes the selected cover. Emergency exit: hold L1 + R1 + touchpad for two seconds.

## Graphics and BIOS

The copied smooth defaults are **4K / 4K ENHANCED / Stretch / Integer Scaling on / VSync off**. Existing explicit choices take precedence. Stretch takes precedence over integer sizing; use Original for the native **10:9** aspect ratio. Resolution/VSync need an app restart; VSync-off requires immediate presentation support from the driver.

The independent edge-aware shader enhances presentation; internal GB/GBC resolution stays 160×144. No HD sprite replacement or platform JIT is used.

mGBA detects the appropriate Game Boy model. An external BIOS is optional: `bios/gb_bios.bin` for DMG or `bios/gbc_bios.bin` for GBC. BIOS skipping is enabled by default. No BIOS or commercial ROM is included.

## Covers

On-demand artwork uses the Libretro [Game Boy](https://thumbnails.libretro.com/Nintendo%20-%20Game%20Boy/Named_Boxarts/) and [Game Boy Color](https://thumbnails.libretro.com/Nintendo%20-%20Game%20Boy%20Color/Named_Boxarts/) collections. Filename/title/region matching uses a bundled 3,160-name index; successful downloads are cached. No-Intro-style names work best. Local PNG/JPEG covers can be placed in `covers/` using the ROM filename without its extension or displayed serial.

## Build and tests

~~~sh
PS5GBC_DEPS=/path/to/prepared/ps5-build bash gbc/tools/build.sh
python3 gbc/tools/test.py
~~~

See [BUILDING.md](BUILDING.md) and [TESTING.md](TESTING.md). First PS5 console validation is pending. Host tests execute original GB/GBC homebrew, verify real video/audio, input, SRAM/state/RTC support, ZIP loading and Vulkan rendering. Camera, motion sensors, multiplayer and general firmware compatibility are not established.

## Credits and license

YAHBALLON / Globaleliteee; Spyros and the PS5SX2/PS5SNES frontend contributors; mGBA contributors; PS5 Vulkan/native tooling, Lapy, Libretro thumbnails and dependency authors.

Frontend/integration: GPL-3.0-or-later. mGBA: MPL-2.0. See [COPYING.GPLv3](COPYING.GPLv3) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This port adds a minimal libretro framebuffer-pointer reset on deinit and a GB-only declaration compatibility header; both are included in the source.
