// (AI-assisted) Original PS5SX2 frontend startup, with a GB/GBC playback backend.
#include "fe_ps5.h"
#include "elevation.hpp"
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
extern "C" int sceNetInit();
extern "C" int sceSystemServiceLoadExec(const char* path, const char* const* argv);
extern "C" int sceKernelUsleep(unsigned int microseconds);
// PS5-native title shutdown. libc exit() can trigger SIGSYS on retail firmware.
extern "C" [[noreturn]] void gbcxy_exit_to_shell(const char* reason) {
    std::printf("[GBCXY] System exit requested: %s\n",reason?reason:"unknown");
    std::fflush(nullptr);
    const int rc=sceSystemServiceLoadExec("exit",nullptr);
    std::printf("[GBCXY] shell exit returned 0x%08x; waiting safely\n",unsigned(rc));
    std::fflush(nullptr);
    for(;;)sceKernelUsleep(100000);
}
extern "C" [[noreturn]] void catchReturnFromMain(int status) {
    std::printf("[GBCXY] CRT main returned status %d\n",status);
    gbcxy_exit_to_shell("CRT return");
}
int main() {
    sceNetInit();
    const auto access=elevation::request(elevation::Capability::filesystem);
    std::string root="/data/PS5GBC";
    if(mkdir(root.c_str(),0777)!=0&&errno!=EEXIST)root="/download0/PS5GBC";
    mkdir(root.c_str(),0777);
    for(const char* dir:{"games","roms","saves","states","settings","covers","cache","logs","screenshots","bios"})mkdir((root+"/"+dir).c_str(),0777);
    mkdir((root+"/cache/ps5vk-shader-cache").c_str(),0777);
    setenv("PS5VK_SHADER_CACHE_DIR",(root+"/cache/ps5vk-shader-cache").c_str(),1);
    int fd=open((root+"/logs/boot.log").c_str(),O_WRONLY|O_CREAT|O_TRUNC|O_APPEND,0666);
    if(fd>=0){dup2(fd,fileno(stdout));dup2(fd,fileno(stderr));close(fd);setvbuf(stdout,nullptr,_IOLBF,4096);}
    std::printf("[boot] GBCXY v2.0.0 by YAHBALLON, original PS5SX2 shelf, filesystem=%u\n",unsigned(access));
    OrbisFrontendPaths paths;paths.top_dir=root;paths.games_dir=root+"/games";paths.settings_dir=root+"/settings";
    paths.gs_ini=root+"/gs.ini";paths.covers_dir=root+"/covers";paths.cache_dir=root+"/cache";
    paths.logs_dir=root+"/logs";paths.settings_log=root+"/logs/settings.log";paths.serial_cache=root+"/cache/serials.txt";
    paths.usb_list=root+"/cache/usb-games.txt";paths.allow_download=true;paths.sound=true;
    paths.report_header="GBCXY v2.0.0 by YAHBALLON";
    for(int i=0;i<8;++i){auto usb="/mnt/usb"+std::to_string(i);
        for(const char* folder:{"/homebrew/PS5GBC/games","/homebrew/PS5GBC/roms","/PS5GBC/games","/PS5GBC/roms","/homebrew/PPSA99210/games","/homebrew/PPSA99210/roms","/GBC","/GB"})paths.usb_dirs.push_back(usb+folder);}
    for(const char* local:{"/data/PS5GBC/games","/data/PS5GBC/roms","/data/GBC","/data/GB","/data/homebrew/PS5GBC/roms","/data/homebrew/PS5GBC/games","/data/homebrew/PPSA99210/games","/data/homebrew/PPSA99210/roms"})paths.usb_dirs.push_back(local);
    orbis_frontend_set_language("/download0/english-language");
    orbis_web_start(paths,"v2.0.0 by YAHBALLON");
    bool ran=false;orbis_frontend_run(paths,"v2.0.0 by YAHBALLON",&ran);
    gbcxy_exit_to_shell("frontend completed");
}
