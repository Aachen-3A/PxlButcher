#include "MuonSelector.hh"


using namespace pxl;
using namespace std;

//--------------------Constructor-----------------------------------------------------------------

MuonSelector::MuonSelector( const Tools::MConfig &cfg ):

    // Muons:
    m_muo_pt_min(                     cfg.GetItem< double >( "Muon.pt.min" ) ),
    m_muo_eta_max(                    cfg.GetItem< double >( "Muon.eta.max" ) ),
    m_muo_invertIso(                  cfg.GetItem< bool   >( "Muon.InvertIsolation" ) ),
    m_muo_iso_type(                   cfg.GetItem< string >( "Muon.Iso.Type" ) ),
    m_muo_iso_max(                    cfg.GetItem< double >( "Muon.Iso.max" ) ),
    m_muo_iso_useDeltaBetaCorr(       cfg.GetItem< bool   >( "Muon.Iso.UseDeltaBetaCorr" ) ),
    m_muo_iso_useRhoCorr(             cfg.GetItem< bool   >( "Muon.Iso.UseRhoCorr" ) ),
    m_muo_id_type(                    cfg.GetItem< string >( "Muon.ID.Type" ) ),
    m_muo_HighPtSwitchPt(             cfg.GetItem< double >( "Muon.ID.HighPtSwitchPt" ) ),
    m_muo_EA( cfg , "Muon.EffectiveArea.File" )
{
}
//--------------------Destructor-----------------------------------------------------------------

MuonSelector::~MuonSelector() {
}


bool MuonSelector::passMuon( pxl::Particle *muon, const bool& isRec ,double rho ) const {
    if( isRec ){
        return muonID(muon, rho);
    }
    //generator muon cuts
    else{
        double const muon_rel_iso = muon->getUserRecord( "GenIso" ).toDouble() / muon->getPt();
        // Gen iso cut.
        bool iso_failed = muon_rel_iso > m_muo_iso_max;
        //turn around for iso-inversion
        if( m_muo_invertIso ) iso_failed = !iso_failed;
        //now check
        if( iso_failed ) return false;
    }
    return true;

}


bool MuonSelector::kinematics(pxl::Particle *muon ) const {
    //pt cut
    if( muon->getPt() < m_muo_pt_min ) return false;
    //eta cut
    if( fabs( muon->getEta() ) > m_muo_eta_max ) return false;

    return true;
}


bool MuonSelector::muonID( pxl::Particle *muon , double rho) const {
    if(kinematics( muon )) return false;
    //the muon cuts are according to :
    //https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMuonId
    //status: 17.9.2014

    // isTightMuon or isHighPtMuon
    if(m_muo_id_type=="musicID"){
        if(muon->getPt()<m_muo_HighPtSwitchPt){
            if( muon->getUserRecord("isTightMuon")) return false;
        }else{
            if( muon->getUserRecord("isHighPtMuon")) return false;
        }
    }else{
        if(muon->getUserRecord(m_muo_id_type)) return false;
    }


    // Muon isolation.
    double muon_iso;
    if( m_muo_iso_type == "Tracker" ) {
      muon_iso = muon->getUserRecord( "TrkIso" );
    } else if( m_muo_iso_type == "PF" ) {
      //[sumChargedHadronPt+ max(0.,sumNeutralHadronPt+sumPhotonPt-0.5sumPUPt]/pt
        if( m_muo_iso_useDeltaBetaCorr && !m_muo_iso_useRhoCorr) {
            muon_iso = muon->getUserRecord( "PFIsoR04ChargedHadrons" ).toDouble()
                + max( 0.,
                    muon->getUserRecord( "PFIsoR04NeutralHadrons" ).toDouble()
                    + muon->getUserRecord( "PFIsoR04Photons" ).toDouble()
                    - 0.5 * muon->getUserRecord( "PFIsoR04PU" ).toDouble()
                );
        } else if (m_muo_iso_useDeltaBetaCorr && !m_muo_iso_useRhoCorr){
            //PFIsoCorr = PF(ChHad PFNoPU) + Max ((PF(Nh+Ph) - ρ’EACombined),0.0)) where ρ’=max(ρ,0.0) and with a 0.5 GeV threshold on neutrals

            double const photonEA = m_muo_EA.getEffectiveArea(          fabs(muon->getEta()), EffectiveArea::photon );
            double const neutralHadronEA = m_muo_EA.getEffectiveArea(   fabs(muon->getEta()), EffectiveArea::neutralHadron );

            muon_iso = muon->getUserRecord( "PFIsoR04ChargedHadrons" ).toDouble()
                + max( 0.,
                    muon->getUserRecord( "PFIsoR04NeutralHadrons" ).toDouble()
                    + muon->getUserRecord( "PFIsoR04Photons" ).toDouble()
                    -  rho* (photonEA+neutralHadronEA)
                );

        } else {
            muon_iso = muon->getUserRecord( "PFIsoR04ChargedHadrons" ).toDouble()
                + muon->getUserRecord( "PFIsoR04NeutralHadrons" ).toDouble()
                + muon->getUserRecord( "PFIsoR04Photons" ).toDouble();
        }
    } else if( m_muo_iso_type == "PFCombined03" ) { //not supported anymore
        if( m_muo_iso_useDeltaBetaCorr ) {
            muon_iso = muon->getUserRecord( "PFIsoR03ChargedHadrons" ).toDouble()
                + max( 0.,
                    muon->getUserRecord( "PFIsoR03NeutralHadrons" ).toDouble()
                    + muon->getUserRecord( "PFIsoR03Photons" ).toDouble()
                    - 0.5 * muon->getUserRecord( "PFIsoR03PU" ).toDouble()
                );
        } else {
            muon_iso = muon->getUserRecord( "PFIsoR03ChargedHadrons" ).toDouble()
                + muon->getUserRecord( "PFIsoR03NeutralHadrons" ).toDouble()
                + muon->getUserRecord( "PFIsoR03Photons" ).toDouble();
        }
    } else if( m_muo_iso_type == "Combined" ) { // not supported anymore
        muon_iso = muon->getUserRecord( "TrkIso" ).toDouble()
            + muon->getUserRecord( "ECALIso" ).toDouble()
            + muon->getUserRecord( "HCALIso" ).toDouble();
    } else {
      throw Tools::config_error( "In passMuon(...): Invalid isolation type: '" + m_muo_iso_type + "'" );
    }

    double const muon_rel_iso = muon_iso / muon->getPt();

    bool iso_failed = muon_rel_iso > m_muo_iso_max;
    //turn around for iso-inversion
    if( m_muo_invertIso ) iso_failed = !iso_failed;
    //now check
    if( iso_failed ) return false;


    //no cut failed
    return true;
}



