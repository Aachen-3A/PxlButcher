#ifndef PHOTONEFFECTIVEAREA
#define PHOTONEFFECTIVEAREA

#include "BinnedMapping.hh"
#include "Tools/MConfig.hh"

class PhotonEffectiveArea {
   public:
      PhotonEffectiveArea( Tools::MConfig const &config );
      ~PhotonEffectiveArea() {}

      double getEffectiveArea( double const eta,
                               unsigned int const type
                               ) const;

      enum EffArea { chargedHadron = 0,
                     neutralHadron = 1,
                     photon = 2
                     };

   private:
      Tools::MConfig const m_EA_config;

      BinnedMapping const m_eta_EAchargedHadrons_map;
      BinnedMapping const m_eta_EAneutralHadrons_map;
      BinnedMapping const m_eta_EAphotons_map;
};

#endif /*PHOTONEFFECTIVEAREA*/
