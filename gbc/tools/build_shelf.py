"""(AI-assisted) PS5GBC out-of-tree core build, native link and signed test package."""
from pathlib import Path
import concurrent.futures,hashlib,json,os,shutil,subprocess,zipfile
project=Path(__file__).resolve().parents[2]
nes=project/'gbc';out=nes/'build-shelf';out.mkdir(exist_ok=True)
core=nes/'third_party/mgba';sdk=Path(os.environ['PS5_PAYLOAD_SDK'])
deps=Path(os.environ['PS5GBC_DEPS']);nfs=Path(os.environ['LIBNFS_PREFIX']);z=Path(os.environ['LIBZ_PREFIX'])
native=project/'ps5/proto/native';wrapper=native/'tooling/prospero-clang18'
host=nes/'build-core-host'
opts=['-DBUILD_LIBRETRO=ON','-DSKIP_LIBRARY=ON','-DDISABLE_DEPS=ON','-DBUILD_QT=OFF','-DBUILD_SDL=OFF','-DBUILD_GL=OFF','-DBUILD_GLES2=OFF','-DBUILD_GLES3=OFF','-DUSE_DEBUGGERS=OFF','-DUSE_GDB_STUB=OFF','-DENABLE_SCRIPTING=OFF','-DM_CORE_GB=ON','-DM_CORE_GBA=OFF','-DUSE_LZMA=OFF','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DCMAKE_C_FLAGS=-include '+str(nes/'ps5-compat/gb_only.h')]
subprocess.run(['cmake','-S',str(core),'-B',str(host),'-G','Ninja','-DCMAKE_C_COMPILER=clang-18',*opts],check=True)
subprocess.run(['cmake','--build',str(host),'--target','mgba-version-info'],check=True)
sources=[Path(e['file']) for e in json.loads((host/'compile_commands.json').read_text()) if 'mgba_libretro.dir' in e['command']]
incs=['-I'+str(nes/'ps5-compat'),'-I'+str(nes/'include'),'-I'+str(core/'include'),'-I'+str(core/'src'),'-I'+str(host/'include')]
base=['-O2','-march=znver2','-ffunction-sections','-fdata-sections','-fno-stack-protector','-fno-plt']
cflags=['-target','x86_64-sie-ps5','-isysroot',str(sdk),'-isystem',str(sdk/'target/include'),'-std=gnu11','-D__LIBRETRO__','-DMGBA_STANDALONE','-DMINIMAL_CORE=2','-DM_CORE_GB','-include',str(nes/'ps5-compat/gb_only.h'),'-DDISABLE_THREADING','-DDISABLE_ANON_MMAP','-DHAVE_STRDUP','-DHAVE_STRNDUP','-DHAVE_LOCALTIME_R','-DHAVE_LOCALE','-DHAVE_XLOCALE','-DHAVE_STRTOF_L','-DHAVE_SETLOCALE','-DHAVE_USELOCALE','-DCOLOR_16_BIT','-DCOLOR_5_6_5','-Wno-implicit-function-declaration',*base,*incs]
def compile_c(path):
    key=str(path.relative_to(core)) if path.is_relative_to(core) else path.name
    obj=out/'obj/core'/Path(key).with_suffix('.o');obj.parent.mkdir(parents=True,exist_ok=True)
    if not obj.exists() or obj.stat().st_mtime < max(path.stat().st_mtime,Path(__file__).stat().st_mtime):
        subprocess.run(['clang-18',*cflags,'-c',str(path),'-o',str(obj)],check=True)
    return obj
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:objects=list(pool.map(compile_c,sources))
print(f'GB/GBC core: {len(objects)} PS5 objects (AI-assisted)',flush=True)
cpp=[*base,'-std=c++20','-fno-exceptions','-fno-rtti','-pthread','-DORBIS_NFS=1','-I'+str(nfs/'include'),
     '-I'+str(z/'include'),'-DORBIS_VULKAN=1','-DORBIS_NES=1','-DORBIS_CURL=1','-DCURL_STATICLIB',
     '-I'+str(project/'3rdparty/vulkan/include'),'-I'+str(project/'3rdparty/include'),
     '-DFE_FONT_DIR="'+str(project/'bin/resources/fonts')+'"','-DFE_ASSET_DIR="'+str(project/'ps5/frontend/assets')+'"','-I'+str(nes/'src'),'-I'+str(project/'ps5/frontend'),
     '-I'+str(project/'ps5/coreorbis/orbis-shims/filesystem-elevation'),*incs]
cpp_sources=[nes/'src'/n for n in ['core_session.cpp','games.cpp','shelf_games.cpp','shelf_runtime.cpp','main_shelf.cpp','loading.cpp','library_cache.cpp','controller_bindings.cpp']]
cpp_sources += [project/'ps5/frontend'/f'{name}.cpp' for name in ['fe_app','fe_covers','fe_renderer','fe_sound','fe_text','fe_vk','fe_ps5','fe_web','fe_i18n','fe_settings','fe_options','fe_exact_porpoise']]
cpp_sources += [project/'ps5/frontend/fe_nfs.cpp',project/'ps5/coreorbis/orbis-shims/filesystem-elevation/src/elevation.cpp']
cpp_sources += [project/'ps5/porpoise_original/src/ui_gfx.cpp']
cpp_sources += [native/'tooling/native'/f'{name}.cpp' for name in ['app_crt','app_cpp_runtime']]
for src in cpp_sources:
    obj=out/'obj'/f'{src.stem}.o';obj.parent.mkdir(exist_ok=True)
    subprocess.run(['sh',str(wrapper),*cpp,'-c',str(src),'-o',str(obj)],check=True);objects.append(obj)

qrcode=out/'obj/qrcodegen.o'
subprocess.run(['clang-18',*cflags,'-I'+str(project/'ps5/frontend/third_party/qrcodegen'),'-c',str(project/'ps5/frontend/third_party/qrcodegen/qrcodegen.c'),'-o',str(qrcode)],check=True)
objects.append(qrcode)
vulkan=deps/'PS5_Vulkan'
mesa=Path(os.environ.get('PS5GBC_MESA_UTIL_DIR',str(out/'mesa-util')))
if not all((mesa/name).exists() for name in ['u_thread.o','anon_file.o','os_file.o']):
    environment=dict(os.environ,PS5_VULKAN_DIR=str(vulkan))
    subprocess.run(['bash',str(project/'ps5/tools/build-mesa-util.sh'),str(mesa),str(sdk)],check=True,env=environment)
for name in ['u_thread.o','anon_file.o','os_file.o']:objects.append(mesa/name)
(out/'vulkan').mkdir(exist_ok=True)
vkarchive=out/'vulkan/libps5vk.ps5.a'
shutil.copy2(vulkan/'build/driver/ps5/libps5vk.ps5.a',vkarchive)
subprocess.run(['llvm-objcopy-18','--redefine-sym','vkGetInstanceProcAddr=ps5vk_driver_vkGetInstanceProcAddr',str(vkarchive)],check=True)
vklibs=[vkarchive,vulkan/'.deps/native/vulkan-runtime/lib/libvk_runtime.ps5.a',vulkan/'build/driver/ps5/libpsbc_driver.ps5.a',vulkan/'.deps/native/psbc/lib/libpsbc_support.ps5.a']
# (AI-assisted) PSBC's make enumerates generated sources before creating them.
# A clean CI checkout therefore misses NIR/SPIR-V/ACO objects without this
# supplemental archive. Use the same known-working PS5MesenX build fix.
environment=dict(os.environ,PS5_VULKAN_DIR=str(vulkan),PS5_PAYLOAD_SDK=str(sdk))
subprocess.run(['python3',str(nes/'tools/build_generated_psbc.py')],env=environment,check=True)
generated_psbc=out/'ps5-core/generated-psbc.ps5.a'
assert generated_psbc.is_file() and generated_psbc.stat().st_size>100
vklibs.append(generated_psbc)
subprocess.run(['python3',str(nes/'tools/build_agc_imports.py')],env=environment,check=True)
agc_dir=out/'ps5-core/agc-imports'
assert all((agc_dir/name).is_file() for name in ['libSceAgc.so','libSceAgcDriver.so'])
netlibs=[z/'lib'/f'lib{name}.a' for name in ['curl','psl','ssl','crypto','zstd','z']]

stubs=sorted(str(p) for p in (sdk/'target/lib').glob('*.so') if p.name not in ('libScePosixForWebKit.so','libSceGLSlimVSH.so'))
# Native AGC modules are provided by the PS5 firmware. Only import stubs
# are used during the host link; never bundle them with the installer.
stubs.extend(str(agc_dir/name) for name in ('libSceAgc.so','libSceAgcDriver.so'))
pie=out/'llvm-pie.elf'
link=['ld.lld-18','-m','elf_x86_64','-pie','-z','max-page-size=0x4000','-mllvm','-emulated-tls',
      '--hash-style=gnu','-T',str(native/'tooling/native/ps5-pie.ld'),
      '-T',str(project/'ps5/coreorbis/orbis-shims/ehframe.ld'),'--eh-frame-hdr',
      '--version-script',str(native/'tooling/native/app-symbols.map'),'--no-dynamic-linker','-e','_start',
      '-o',str(pie),*(str(p) for p in objects),str(nfs/'lib/libnfs.a'),'--whole-archive',*(str(p) for p in vklibs),'--no-whole-archive','--start-group',*(str(p) for p in netlibs),'--end-group',
      '--as-needed',*stubs,'-L'+str(sdk/'target/lib'),
      *(str(sdk/'target/lib'/f'lib{lib}.a') for lib in ['c++','c++abi','unwind','c']),'-lpthread']
subprocess.run(link,check=True)
exports=out/'orbis-exports.map'
subprocess.run(['python3',str(project/'ps5/genmap.py'),str(pie),str(sdk/'target/lib'),str(exports)],check=True)
subprocess.run(link+['--version-script',str(exports)],check=True)
# (AI-assisted) Build the project's PS5SX2 native writer, never the driver helper:
# it emits the already-tested flexible/internal memory process parameters.
tool=out/'host/ps5-native-tool';tool.parent.mkdir(exist_ok=True)
subprocess.run(['clang++-18','-std=c++20','-O2','-o',str(tool),
                *(str(native/'tooling/native'/f'{name}.cpp') for name in
                  ['native_app_builder','elf_object','self_container','sce_module_writer']),'-lz'],check=True)
subprocess.run([str(tool),'link','--in',str(pie),'--out',str(out/'eboot.elf'),'--stub-dir',str(sdk/'target/lib'),
                '--stub',str(agc_dir/'libSceAgc.so'),'--stub',str(agc_dir/'libSceAgcDriver.so'),
                '--module-sdk','0x02000009','--companion-sdk','0x08050001','--file-name','eboot.elf'],check=True)
subprocess.run(['python3',str(nes/'tools/check_memory.py'),str(out/'eboot.elf')],check=True)
subprocess.run(['python3',str(project/'ps5/tools/prepare_console_elf.py'),'--input',str(out/'eboot.elf'),
                '--output',str(out/'eboot-console-ready.elf')],check=True)
# Recreate only the generated app folder so stale files cannot enter a release.
app=out/'package/PPSA99210'
if app.exists():
    if app.is_symlink() or app.resolve() != (out.resolve()/'package/PPSA99210'):
        raise RuntimeError('Unsafe package output path')
    shutil.rmtree(app)
(app/'sce_module').mkdir(parents=True,exist_ok=True)
subprocess.run([str(tool),'self','--sign','--in',str(out/'eboot.elf'),'--out',str(app/'eboot.bin'),'--magic','0x1D3D154F'],check=True)
subprocess.run([str(tool),'self','--inspect','--file',str(app/'eboot.bin')],check=True)
shutil.copytree(nes/'sce_sys',app/'sce_sys',dirs_exist_ok=True)
shutil.copy2(deps/'PS5_Vulkan/runtime/libc.prx',app/'sce_module/libc.prx')
# Upstream's historical Lapy commit is no longer fetchable. Reuse only the
# exact-title helper already included in our previous independently verified
# release, after checking the entire archive's pinned SHA-256 in CI.
baseline=os.environ.get('PS5GBC_LAPY_BASELINE')
if not baseline:
    raise RuntimeError('PS5GBC_LAPY_BASELINE is required: pinned prior PPSA99210 release ZIP')
baseline=Path(baseline)
with zipfile.ZipFile(baseline) as archive:
    names=set(archive.namelist())
    for name in ['lapy.elf','lapy-manifest.json']:
        item='PPSA99210/'+name
        if item not in names:raise RuntimeError('Missing verified Lapy helper: '+item)
        (app/name).write_bytes(archive.read(item))
    license_name='PPSA99210/licenses/Lapy-MIT.txt'
    if license_name not in names:raise RuntimeError('Lapy MIT license missing in pinned release')
    (out/'filesystem-helper').mkdir(exist_ok=True)
    (out/'filesystem-helper/Lapy-MIT.txt').write_bytes(archive.read(license_name))
lapy=json.loads((app/'lapy-manifest.json').read_text())
if lapy.get('target_title')!='PPSA99210' or lapy.get('mode')!='elf-helper':
    raise RuntimeError('Pinned Lapy helper has invalid target-title or mode')
if lapy.get('elf_sha256')!=hashlib.sha256((app/'lapy.elf').read_bytes()).hexdigest():
    raise RuntimeError('Pinned Lapy helper ELF does not match its manifest')
if (app/'lapy.elf').read_bytes()[:6]!=b'\x7fELF\x02\x01':
    raise RuntimeError('Pinned Lapy helper is not an ELF64 executable')
licenses=app/'licenses';licenses.mkdir(exist_ok=True)
for path,name in [(core/'LICENSE','mGBA-MPL-2.0.txt'),(project/'COPYING.GPLv3','GPLv3.txt'),
                  (out/'filesystem-helper/Lapy-MIT.txt','Lapy-MIT.txt'),(deps/'libnfs/COPYING','libnfs.txt')]:
    if not path.is_file():
        raise FileNotFoundError(f'Required license missing: {path}')
    shutil.copy2(path,licenses/name)
if (nes/'licenses').exists():
    shutil.copytree(nes/'licenses',licenses,dirs_exist_ok=True)
revision_file=core/'UPSTREAM_REVISION.txt'
if revision_file.exists():commit=revision_file.read_text().strip()
else:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=core,text=True).strip()
manifest={'ai_assisted':True,'name':'GBCXY v2.0.0 by YAHBALLON','title':'PPSA99210','core':'mGBA 0.10.5 portable GB/GBC',
          'frontend':'GBCXY native Porpoise 3D CoverFlow (5 themes)',
          'frontend_source_sha256':{str(p.relative_to(project)):hashlib.sha256(p.read_bytes()).hexdigest() for p in cpp_sources if '/ps5/frontend/' in str(p)},
          'core_commit':commit,'core_source':'https://github.com/mgba-emu/mgba','console_tested':False,
          'files':{str(p.relative_to(app)):hashlib.sha256(p.read_bytes()).hexdigest() for p in app.rglob('*')
                   if p.is_file() and p.name != 'build-manifest.json'}}
(app/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
shutil.copy2(project/'INSTALL.md',out/'package/INSTALL.md')
bundle=out/'GBCXY-v2.0.0-by-YAHBALLON.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(app.rglob('*')):
        if path.is_file():archive.write(path,Path('PPSA99210')/path.relative_to(app))
    archive.write(project/'INSTALL.md','INSTALL.md')
print('GBCXY signed native test package:',bundle,flush=True)
