#include "EffectiveArea.hh"

#include <cmath>
#include <string>
#include <sstream>

#include "Tools/Tools.hh"

EffectiveArea::EffectiveArea( Tools::MConfig const &config , std::string ObjectName) :

   m_eta_EAchargedHadrons_map( config,
                               ObjectName + ".EffArea.eta_edges",
                               ObjectName + ".EffArea.EA_charged_hadrons",
                               ObjectName + ".EffArea.abs_eta" ),
   m_eta_EAneutralHadrons_map( config,
                               ObjectName + ".EffArea.eta_edges",
                               ObjectName + ".EffArea.EA_neutral_hadrons",
                               ObjectName + ".EffArea.abs_eta" ),
   m_eta_EAphotons_map(        config,
                               ObjectName + ".EffArea.eta_edges",
                               ObjectName + ".EffArea.EA_photons",
                               ObjectName + ".EffArea.abs_eta" )
{
}

double EffectiveArea::getEffectiveArea( double const eta,
                                              unsigned int const type
                                              ) const {
   if( type == chargedHadron ) return m_eta_EAchargedHadrons_map.getValue( eta );
   if( type == neutralHadron ) return m_eta_EAneutralHadrons_map.getValue( eta );
   if( type == photon        ) return m_eta_EAphotons_map.getValue( eta );

   std::stringstream err;
   err << "[ERROR] (EffectiveArea): Not supported type = "<< type << "!" << std::endl;
   throw Tools::value_error( err.str() );
}
