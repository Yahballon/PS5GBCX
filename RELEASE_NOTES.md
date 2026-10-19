# GBCXY v2.0.0 by YAHBALLON

- Updated Game Boy and Game Boy Color app with a 3D Porpoise-inspired CoverFlow, five bespoke GBCXY visual themes, natural-size cover art, automatic local/cache/Libretro GB and GBC box art resolution.
- Original **Chromatic Pocket** animated loading screen with scanned game and folder counts.
- Safe in-app confirmation and PS5 native title exit using `sceSystemServiceLoadExec("exit", nullptr)` instead of libc `exit(0)`.
- Compatible mGBA GB/GBC core, input remapping, battery saves, state saves, RTC and ROM loading from internal, USB and NFS sources.
- **Title ID `PPSA99210` and data path `/data/PS5GBC/` are unchanged** so existing installs, ROMs and saves survive this upgrade.
- Genuine signed native `eboot.bin` and `PPSA99210.zip` created from the GitHub workflow; CI verifies archive CRC, manifest hashes, metadata and source assets.

**Console smoke test still required:** Successful GitHub compilation verifies the package structure, not runtime compatibility on every jailbroken PS5. No commercial ROMs are included.
