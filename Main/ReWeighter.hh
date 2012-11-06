#include "Tools/PXL/PXL.hh"

namespace Tools {
   class MConfig;
}

// CMSSW include:
#include "PhysicsTools/Utilities/interface/Lumi3DReWeighting.h"


class ReWeighter {
public:
   ReWeighter( const Tools::MConfig &cutconfig  );
   ~ReWeighter() {}

   void ReWeightEvent( const pxl::Event &event );

private:
   edm::Lumi3DReWeighting m_LumiWeights;
   const bool m_useGenWeights;
   const bool m_usePileUpReWeighting;
};