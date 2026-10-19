// GBCXY CHROMATIC POCKET: original 8-bit four-color pixel carousel animation.
// Native PS5 Vulkan UI only, no video, network assets or CPU-side images.
#include "loading.h"
#include "gbcxy_build_version.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <string>

namespace gbc {
namespace {
constexpr float pi=3.14159265358979f;
uint32_t RGBA(uint8_t r,uint8_t g,uint8_t b,uint8_t a=255) {
    return uint32_t(r)|(uint32_t(g)<<8)|(uint32_t(b)<<16)|(uint32_t(a)<<24);
}
float wave(float t){return (std::sin(t)+1.f)*0.5f;}
}
void BuildLoadingFrame(fe::FrameDesc& frame,const fe::Fonts& font,unsigned width,unsigned height,
                       const ScanProgress& progress,double elapsed,bool done) {
    frame=fe::FrameDesc{};
    if(!width||!height)return;
    const float W=float(width),H=float(height),k=H/2160.f,t=float(elapsed);
    const float top[4]={0.003f,0.017f,0.047f,1.f};
    const float mid[4]={0.012f,0.042f,0.082f,1.f};
    const float bottom[4]={0.002f,0.014f,0.030f,1.f};
    std::copy(top,top+4,frame.bg.top);
    std::copy(mid,mid+4,frame.bg.mid);
    std::copy(bottom,bottom+4,frame.bg.bottom);
    frame.bg.glow_color[0]=0.08f;frame.bg.glow_color[1]=0.70f;frame.bg.glow_color[2]=0.79f;frame.bg.glow_color[3]=0.32f;
    frame.bg.glow_pos[0]=0.5f;frame.bg.glow_pos[1]=0.43f;frame.bg.glow_pos[2]=0.75f;frame.bg.glow_pos[3]=0.48f;
    frame.bg.floor_glow[0]=0.13f;frame.bg.floor_glow[1]=0.90f;frame.bg.floor_glow[2]=0.56f;frame.bg.floor_glow[3]=0.08f;
    frame.bg.misc[0]=W/H;frame.bg.misc[1]=0.85f;frame.bg.misc[2]=0.47f;frame.bg.misc[3]=t;
    frame.time=t;
    auto& ui=frame.ui;ui.reserve(2600);
    const auto white=RGBA(250,252,255),pale=RGBA(160,194,227);
    const std::array<uint32_t,4> col={
        RGBA(242,84,171),RGBA(75,238,189),RGBA(250,205,79),RGBA(134,127,255)};
    auto rect=[&](float x,float y,float w,float h,float rad,uint32_t color){
        if(w>0&&h>0)fe::Fonts::AddRoundedRect(ui,x,y,w,h,rad,color);
    };
    auto text=[&](const std::string& s,float x,float y,float size,uint32_t color,
                  float weight=0.f,fe::Fonts::Align a=fe::Fonts::Left){
        font.AddText(ui,s.c_str(),x,y,size*k,color,weight,a);
    };
    // Header and moving status ticker.
    rect(94*k,112*k,9*k,142*k,4*k,col[0]);
    text("GBCXY",142*k,198*k,110,white,0.70f);
    text(std::string("by YAHBALLON  /  v")+gbcxy_build::kVersion,
         144*k,262*k,34,pale,0.16f);
    text(done?"COLOR SYSTEM READY":"BOOTING COLOR SYSTEM",
         W-115*k,173*k,35,done?col[1]:col[0],0.36f,fe::Fonts::Right);
    const float trace=std::fmod(t*440.f*k,W+160*k)-80*k;
    rect(0,0,W,6*k,0,RGBA(11,75,140));
    rect(trace,0,160*k,8*k,3*k,col[1]);
    // CHROMATIC POCKET: rotating 4-color LCD pixel field and scan lines.
    // Square panel is inspired by the original Game Boy Color 160x144
    // screen proportions, not GBAXY's 3:2 horizontal sine ribbons.
    const float cx=W*0.5f,cy=H*0.423f;
    const float viewW=765*k,viewH=705*k;
    rect(cx-viewW*0.5f-27*k,cy-viewH*0.5f-27*k,
         viewW+54*k,viewH+54*k,43*k,RGBA(188,105,253,78));
    rect(cx-viewW*0.5f,cy-viewH*0.5f,viewW,viewH,38*k,RGBA(21,13,53,222));
    rect(cx-viewW*0.5f+23*k,cy-viewH*0.5f+23*k,
         viewW-46*k,viewH-46*k,25*k,RGBA(27,22,65,214));
    const float pulse=wave(t*2.8f);
    // The central pixels oscillate as a circular color mosaic.
    for(int row=0;row<18;++row) {
        for(int column=0;column<19;++column) {
            const float dx=float(column-9),dy=float(row)-8.5f;
            const float dist=std::sqrt(dx*dx+dy*dy);
            const float spin=std::atan2(dy,dx)+t*0.74f;
            const float power=wave(dist*0.83f-spin*3.0f);
            const int palette=(column/4+row/4+int(t*0.6f))%4;
            const float size=(6.f+4.f*power)*k;
            rect(cx+dx*33*k-size*0.5f,cy+dy*33*k-size*0.5f,
                 size,size,1*k,dist>2.9f?col[palette]:RGBA(94,88,159,58));
        }
    }
    for(int band=0;band<5;++band){
        const float sweep=std::fmod(t*92*k+band*149*k,viewH);
        rect(cx-viewW*0.45f,cy-viewH*0.5f+sweep,
             viewW*0.9f,2.2f*k,0,RGBA(166,127,255,48));
    }
    // Chunky cartridges fly in from the distant edges, while the center
    // stays readable; distinct from NESYX's reactor and SNESXY's Hypercube.
    for(int j=0;j<12;++j) {
        float q=std::fmod((j*0.079f)+t*(0.055f+0.009f*(j%3)),1.f);
        const float x=cx+(q-0.5f)*W*0.82f;
        const float y=cy+std::sin(q*2*pi+j)*208*k;
        const float a=3*k+q*14*k;
        rect(x-a*0.5f,y-a*0.5f,a,a,1*k,
             j%2?RGBA(83,252,171,112):RGBA(68,167,254,107));
    }
    // A self-drawn 8-bit Color cartridge appears above the rotating mosaic.
    const float crestW=210*k,crestH=245*k;
    const float crestX=cx-crestW*0.5f,crestY=cy-crestH*0.5f;
    rect(crestX-14*k,crestY-14*k,crestW+28*k,crestH+28*k,29*k,
         RGBA(226,96,241,uint8_t(59+86*pulse)));
    rect(crestX,crestY,crestW,crestH,22*k,RGBA(10,16,49,247));
    rect(crestX+20*k,crestY+17*k,crestW-40*k,9*k,3*k,col[3]);
    rect(crestX+18*k,crestY+crestH-29*k,crestW-36*k,11*k,3*k,col[1]);
    // Pixel C emblem: own geometry, no Nintendo logo or copyrighted art.
    for(int row=0;row<9;++row)for(int column=0;column<7;++column){
        const bool lit=(row==0||row==8)?(column>=2&&column<=5):
                       ((column==1)&&(row>=1&&row<=7));
        if(!lit)continue;
        const float ps=17*k,gap=5*k;
        rect(cx-(7*ps+6*gap)*0.5f+column*(ps+gap),
             cy-(9*ps+8*gap)*0.5f+row*(ps+gap),ps,ps,1*k,col[row%4]);
    }
    // Status panel, sourced from the live NFS/local/USB scan, not fake %. 
    text(done?"COLOR LIBRARY READY":"SCANNING GB / GBC LIBRARY",
         cx,H*0.729f,72,white,0.5f,fe::Fonts::Center);
    text(std::to_string(progress.games)+" GAMES  /  "+
         std::to_string(progress.entries)+" FILES READ",
         cx,H*0.772f,36,pale,0.25f,fe::Fonts::Center);
    const float bx=cx-820*k,bw=1640*k,by=H*0.805f;
    rect(bx,by,bw,19*k,10*k,RGBA(48,62,108));
    const bool measured=progress.sources_total>0;
    const float ratio=done?1.f:(measured?
        std::clamp(float(progress.sources_done)/float(progress.sources_total),0.f,1.f):0.f);
    if(done||measured) {
        if(ratio>0)rect(bx,by,bw*ratio,19*k,10*k,col[1]);
    } else {
        const float travel=wave(t*2.5f);
        rect(bx+travel*(bw-260*k),by,260*k,19*k,10*k,col[0]);
    }
    std::string dir=progress.directory.empty()?"Looking for .gb and .gbc cartridges...":progress.directory;
    if(dir.size()>105)dir="..."+dir.substr(dir.size()-102);
    text(dir,cx,H*0.860f,31,pale,0.12f,fe::Fonts::Center);
    text("FOLDERS CHECKED   "+std::to_string(progress.sources_done)+
         " / "+std::to_string(progress.sources_total),
         cx,H*0.906f,34,done?col[1]:col[0],0.26f,fe::Fonts::Center);
    text("GBCXY  //  CHROMATIC POCKET",W-108*k,H*0.967f,27,RGBA(138,171,209),0.20f,fe::Fonts::Right);
}
} // namespace gba
