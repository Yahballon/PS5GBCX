// GBCXY: individual native box dimensions for landscape and portrait artwork.
// Keeps aspect ratio (no stretching), adjusting the case itself instead of
// clipping large parts of horizontally composed Super Nintendo box art.
// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <algorithm>
#include <cmath>

namespace fe {
inline constexpr float kGBCXYDefaultBoxRatio = 3.0f/4.0f;
struct GBCXYCoverSize { float width=0.0f, height=0.0f; };

inline float GBCXYImageRatio(int width,int height) {
    return width>0 && height>0 ? float(width)/float(height) : kGBCXYDefaultBoxRatio;
}

// Compute the game case itself: max width limits crowding but rescales BOTH
// axes together. Portrait pictures keep their full vertical size; landscape
// gets wider frames. No crop or artificial letterbox is required for art.
inline GBCXYCoverSize GBCXYCaseSize(float ratio,float targetHeight,
                                      float maxWidth,float scale=1.0f) {
    if(!std::isfinite(ratio)||ratio<=0.0f)ratio=kGBCXYDefaultBoxRatio;
    if(!std::isfinite(targetHeight)||targetHeight<=0.0f||
       !std::isfinite(maxWidth)||maxWidth<=0.0f||
       !std::isfinite(scale)||scale<=0.0f)return {};
    const float width=targetHeight*ratio;
    const float fit=std::min(1.0f,maxWidth/width);
    return {width*fit*scale,targetHeight*fit*scale};
}

// Fit the fallback icon INSIDE the landscape case without stretching it.
// The artwork textures themselves always use the complete [0,1] UV domain.
inline GBCXYCoverSize GBCXYFitInside(float imageRatio,float frameWidth,float frameHeight) {
    if(!std::isfinite(imageRatio)||imageRatio<=0.0f)imageRatio=1.0f;
    if(frameWidth<=0.0f||frameHeight<=0.0f)return {};
    const float factor=std::min(frameWidth/imageRatio,frameHeight);
    return {factor*imageRatio,factor};
}
} // namespace fe
