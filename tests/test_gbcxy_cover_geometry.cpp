#include "fe_gbcxy_cover_aspect.h"
#include <cassert>
#include <cmath>
int main(){
  auto portrait=fe::GBCXYCaseSize(fe::GBCXYImageRatio(600,940),448,440);
  assert(portrait.width<portrait.height);
  assert(std::fabs(portrait.width/portrait.height-600.f/940.f)<0.001f);
  auto landscape=fe::GBCXYCaseSize(1.5f,448,440);
  assert(landscape.width>landscape.height&&landscape.width<=440);
  auto square=fe::GBCXYFitInside(1.0f,landscape.width,landscape.height);
  assert(std::fabs(square.width-square.height)<0.001f);
}
