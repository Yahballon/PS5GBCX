// (AI-assisted) GB/GBC core/video/audio integration, preserving the original shelf renderer.
#include "shelf_runtime.h"
#include "graphics.h"
#include "games.h"
#include "fe_settings.h"
#include <array>
#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstring>
#include <mutex>
#include <thread>
#include <time.h>
extern "C" {int sceAudioOutInit();int sceAudioOutOpen(int,int,int,unsigned,unsigned,unsigned);
int sceAudioOutOutput(int,const void*);int sceAudioOutClose(int);}
namespace gbc {
class ShelfAudio {
    std::array<int16_t,48000> ring{};size_t read_at=0,write_at=0;
    int handle=-1;std::mutex mutex;std::atomic<bool> quit{false};std::thread thread;
public:
    bool Open() {sceAudioOutInit();handle=sceAudioOutOpen(255,0,0,256,48000,1);if(handle<0)return false;
        thread=std::thread([this]{alignas(64) int16_t block[512];while(!quit){std::memset(block,0,sizeof(block));
            {std::lock_guard<std::mutex> lock(mutex);for(unsigned i=0;i<512&&read_at!=write_at;++i){block[i]=ring[read_at];read_at=(read_at+1)%ring.size();}}
            if(sceAudioOutOutput(handle,block)<0){timespec pause{0,5000000};nanosleep(&pause,nullptr);}}});return true;}
    void Push(const std::vector<int16_t>& samples) {std::lock_guard<std::mutex> lock(mutex);
        for(size_t i=0;i+1<samples.size();i+=2){size_t a=(write_at+1)%ring.size(),b=(a+1)%ring.size();
            if(a==read_at||b==read_at)break;ring[write_at]=samples[i];ring[a]=samples[i+1];write_at=b;}}
    ~ShelfAudio(){quit=true;if(thread.joinable())thread.join();if(handle>=0)sceAudioOutClose(handle);}
};
ShelfRuntime::ShelfRuntime(const std::string& directory,const fe::Fonts* text):core(directory+"/saves"),root(directory),fonts(text){}
ShelfRuntime::~ShelfRuntime()=default;
bool ShelfRuntime::Start(const std::string& path,fe::Renderer& renderer) {
    error.clear();std::vector<uint8_t> rom;if(!ReadRom(path,rom,error))return false;
    std::map<std::string,std::string> options;
    auto read=[&](const std::string& file){std::string text;fe::settings::ReadFile(file,text);
        for(const auto& item:fe::settings::ReadState(text).kv)options[item.first]=item.second;};
    read(root+"/gs.ini");std::string file=path.substr(path.find_last_of('/')+1);file.resize(file.find_last_of('.'));
    read(root+"/settings/"+file+".ini");
    auto get=[&](const std::string& key,const std::string& fallback){auto at=options.find(key);return at==options.end()?fallback:at->second;};
    core.SetOption("mgba_gb_model","Autodetect");core.SetOption("mgba_use_bios","ON");core.SetOption("mgba_skip_bios","ON");
    aspect=get("GBC/Aspect","Stretch");bindings.Load(options);sound=get("GBC/Sound","true")=="true";
    mode=get("GBC/Graphics","Enhanced");integer=get("GBC/Integer","true")=="true";
    sharpness=std::clamp(float(atof(get("GBC/Sharpness","25").c_str()))/100,0.f,1.f);
    boost=std::clamp(float(atof(get("GBC/ColorBoost","15").c_str()))/100,0.f,1.f);
    contrast=std::clamp(float(atof(get("GBC/Contrast","105").c_str()))/100,0.5f,1.5f);
    correction=get("GBC/ColorCorrection","false")=="true";
    fps_counter=get("GBC/FPS","false")=="true";
    if(!core.Load(path,std::move(rom))){error=core.error;return false;}
    resampler.Reset(core.sample_rate);
    if(sound){audio=std::make_unique<ShelfAudio>();if(!audio->Open()){error="GB/GBC audio port failed";audio.reset();}}
    menu_atlas=renderer.Atlas();active=true;previous=0;accumulated=0;last_save=0;
    return true;
}
void ShelfRuntime::Stop(fe::Renderer& renderer) {
    if(!core.Unload())error=core.error;
    audio.reset();renderer.SetAtlas(menu_atlas);
    for(unsigned i=0;i<3;++i){if(game_sets[i])renderer.FreeTextureSet(game_sets[i]);if(game_textures[i])renderer.DestroyTexture(game_textures[i]);game_sets[i]=VK_NULL_HANDLE;game_textures[i]=nullptr;}active=false;
}
bool ShelfRuntime::Build(fe::Renderer& renderer,fe::FrameDesc& frame,uint32_t raw,double now) {
    const auto input=bindings.Update(raw,now);
    if(input.menu){Stop(renderer);return false;}
    if(input.save||input.load) {
        const bool okay=input.save?core.SaveState():core.LoadState();
        if(!okay)error=core.error;
        std::printf("[gbc] state %s: %s\n",input.save?"save":"load",okay?"OK":core.error.c_str());
    }
    core.buttons[0]=input.joypad;
    if(previous==0){previous=now;last_save=now;accumulated=1/core.fps;}
    accumulated+=std::clamp(now-previous,0.0,0.1)*(input.fast_forward?3.0:1.0);previous=now;
    bool changed=false;unsigned runs=0;
    while(accumulated>=1/core.fps&&runs++<6){core.Run();if(audio&&!input.fast_forward)audio->Push(resampler.Process(core.audio));accumulated-=1/core.fps;changed=true;}
    if(now-last_save>=5){if(!core.SaveBattery())error=core.error;last_save=now;}
    // (AI-assisted) Deferred texture retirement uses the existing renderer's fenced frame slots.
    // Continuous menu/game transitions still need proper testing on PS5 hardware.
    if(changed&&!core.pixels.empty()) {
        // Safely rotate three PS5 Vulkan upload slots; don't use removed
        // UpdateTexture API or mutate an image still in flight.
        const unsigned next=(texture_slot+1)%3;
        fe::Texture* fresh=renderer.CreateTexture(core.width,core.height,
            VK_FORMAT_R8G8B8A8_UNORM,core.pixels.data());
        if(!fresh){error="GB/GBC frame texture creation failed";Stop(renderer);return false;}
        VkDescriptorSet fresh_set=renderer.AllocTextureSet(fresh,fresh,fresh);
        if(!fresh_set){
            renderer.DestroyTexture(fresh);
            error="GB/GBC frame descriptor creation failed";Stop(renderer);return false;
        }
        if(game_sets[next])renderer.FreeTextureSet(game_sets[next]);
        if(game_textures[next])renderer.DestroyTexture(game_textures[next]);
        game_sets[next]=fresh_set;
        game_textures[next]=fresh;
        texture_slot=next;
        ++fps_frames;if(now-fps_time>=1){measured_fps=fps_frames/float(now-fps_time);fps_frames=0;fps_time=now;}
    }
    frame=fe::FrameDesc{};frame.fade=1;
    frame.bg.glow_pos[2]=frame.bg.glow_pos[3]=1;
    frame.bg.floor_glow[2]=frame.bg.floor_glow[3]=1;
    frame.bg.misc[0]=float(renderer.width())/renderer.height();frame.bg.misc[1]=0.5f;
    const auto vp=GameViewport(renderer.width(),renderer.height(),aspect=="Stretch",integer);const float width=vp.width,height=vp.height,x=vp.x,y=vp.y;
    auto vertex=[&](float x,float y,float u,float v){return fe::UiVertex{x,y,u,v,0xffffffff,sharpness,boost,contrast,mode=="Original"?2.f:mode=="Smooth"?3.f:correction?5.f:4.f};};
    frame.ui={vertex(x,y,0,0),vertex(x+width,y,1,0),vertex(x,y+height,0,1),
              vertex(x,y+height,0,1),vertex(x+width,y,1,0),vertex(x+width,y+height,1,1)};
    frame.game_set=game_sets[texture_slot];frame.game_vertices=6;
    if(fps_counter&&fonts){char text[64];std::snprintf(text,sizeof(text),"GB/GBC %.2f FPS / core %.2f",measured_fps,core.fps);fonts->AddText(frame.ui,text,24,40,24,0xffffffff);}
    return true;
}
}
