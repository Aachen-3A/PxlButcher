#include "MuonSelector.hh"

using namespace std;

//--------------------Constructor-----------------------------------------------------------------

MuonSelector::MuonSelector( const Tools::MConfig &cfg ):
    // General
    m_muo_id_type(                    cfg.GetItem< std::string >( "Muon.ID.Type" , "TightID")),
    m_muo_ptSwitch(                   cfg.GetItem< double >( "Muon.ID.PtSwitch" , 200 ) ),
    m_muo_pt_min(                     cfg.GetItem< double >( "Muon.Pt.min" ) ),
    m_muo_eta_max(                    cfg.GetItem< double >( "Muon.Eta.max" ) ),
    m_muo_invertIso(                  cfg.GetItem< bool   >( "Muon.InvertIsolation" ) ),

    // Isolation
    m_muo_iso_type(                   cfg.GetItem< string >( "Muon.Iso.Type" ) ),
    m_muo_iso_max(                    cfg.GetItem< double >( "Muon.Iso.max" ) ),
    m_muo_iso_useDeltaBetaCorr(       cfg.GetItem< bool   >( "Muon.Iso.UseDeltaBetaCorr" , false ) ),
    m_muo_iso_useRhoCorr(             cfg.GetItem< bool   >( "Muon.Iso.UseRhoCorr" , false ) ),

    // Effective area
    m_muo_EA( cfg , "Muon" ),

    // Soft ID
    m_muo_softid_useBool(					cfg.GetItem< bool >("Muon.SoftID.UseBool")),
    m_muo_softid_boolName(				    cfg.GetItem< string >("Muon.SoftID.BoolName")),
    m_muo_softid_isGoodMuon( 			    cfg.GetItem< bool >("Muon.SoftID.IsGoodMuon")),
    m_muo_softid_trackerLayersWithMeas_min( cfg.GetItem< int >("Muon.SoftID.TrackerLayersWithMeas.min")),
    m_muo_softid_pixelLayersWithMeas_min(   cfg.GetItem< int >("Muon.SoftID.PixelLayersWithMeas.min")),
    m_muo_softid_QualityInnerTrack( 		cfg.GetItem< bool >("Muon.SoftID.QualityInnerTrack")),
    m_muo_softid_dxy_max(					cfg.GetItem< double >("Muon.SoftID.Dxy.max")),
    m_muo_softid_dz_max(					cfg.GetItem< double >("Muon.SoftID.Dz.max")),

    // Medium ID
    m_muo_mediumid_useBool(					    cfg.GetItem< bool >("Muon.MediumID.UseBool")),
    m_muo_mediumid_boolName(				    cfg.GetItem< string >("Muon.MediumID.BoolName")),
    m_muo_mediumid_isLooseMuon( 			    cfg.GetItem< bool >("Muon.MediumID.IsLooseMuon")),
    m_muo_mediumid_validFraction_min(		    cfg.GetItem< double >("Muon.MediumID.ValidFraction.min")),
    m_muo_mediumid_isGlobalMuon(			    cfg.GetItem< bool >("Muon.MediumID.IsGlobalMuon")),
    m_muo_mediumid_normalizedChi2_max(		    cfg.GetItem< double >("Muon.MediumID.NormalizedChi2.max")),
    m_muo_mediumid_chi2LocalPosition_max(	    cfg.GetItem< double >("Muon.MediumID.Chi2LocalPosition.max")),
    m_muo_mediumid_trkKink_max(		            cfg.GetItem< double >("Muon.MediumID.TrkKink.max")),
    m_muo_mediumid_segCompGlobal_min(		    cfg.GetItem< double >("Muon.MediumID.SegCompGlobal.min")),
    m_muo_mediumid_segCompTight_min(		    cfg.GetItem< double >("Muon.MediumID.SegCompTight.min")),

    // Tight ID
    m_muo_tightid_useBool(					cfg.GetItem< bool >("Muon.TightID.UseBool")),
    m_muo_tightid_boolName(					cfg.GetItem< string >("Muon.TightID.BoolName")),
    m_muo_tightid_isGlobalMuon(				cfg.GetItem< bool >("Muon.TightID.IsGlobalMuon")),
    m_muo_tightid_isPFMuon(					cfg.GetItem< bool >("Muon.TightID.IsPFMuon")),
    m_muo_tightid_normalizedChi2_max(		cfg.GetItem< double >("Muon.TightID.NormalizedChi2.max")),
    m_muo_tightid_vHitsMuonSys_min(			cfg.GetItem< int >("Muon.TightID.VHitsMuonSys.min")),
    m_muo_tightid_nMatchedStations_min(		cfg.GetItem< int >("Muon.TightID.NMatchedStations.min")),
    m_muo_tightid_dxy_max(					cfg.GetItem< double >("Muon.TightID.Dxy.max")),
    m_muo_tightid_dz_max(					cfg.GetItem< double >("Muon.TightID.Dz.max")),
    m_muo_tightid_vHitsPixel_min(			cfg.GetItem< int >("Muon.TightID.VHitsPixel.min")),
    m_muo_tightid_trackerLayersWithMeas_min(cfg.GetItem< int >("Muon.TightID.TrackerLayersWithMeas.min")),

    // High Pt ID
    m_muo_highptid_useBool(             cfg.GetItem< bool >("Muon.HighPtID.UseBool")),
    m_muo_highptid_boolName(            cfg.GetItem< string >("Muon.HighPtID.BoolName")),
    m_muo_highptid_isGlobalMuon(        cfg.GetItem< bool >("Muon.HighPtID.IsGlobalMuon")),
    m_muo_highptid_ptRelativeError_max( cfg.GetItem< double >("Muon.HighPtID.PtRelativeError.max")),
    m_muo_highptid_nMatchedStations_min(cfg.GetItem< int >("Muon.HighPtID.NMatchedStations.min")),
    m_muo_highptid_vHitsMuonSys_min(    cfg.GetItem< int >("Muon.HighPtID.VHitsMuonSys.min")),
    m_muo_highptid_vHitsPixel_min(      cfg.GetItem< int >("Muon.HighPtID.VHitsPixel.min")),
    m_muo_highptid_vHitsTracker_min(    cfg.GetItem< int >("Muon.HighPtID.VHitsTracker.min")),
    m_muo_highptid_dxy_max(             cfg.GetItem< double >("Muon.HighPtID.Dxy.max")),
    m_muo_highptid_dz_max(              cfg.GetItem< double >("Muon.HighPtID.Dz.max"))
{
    // nothing to do here
}
//--------------------Destructor-----------------------------------------------------------------

MuonSelector::~MuonSelector() {
}


int MuonSelector::passMuon( pxl::Particle *muon, const bool& isRec ,double const rho ) const{
    if( isRec ){
        return muonID(muon, rho);
    } else {
        //generator muon cuts
        double const muon_rel_iso = muon->getUserRecord( "GenIso" ).toDouble() / muon->getPt();
        // Gen iso cut.
        bool iso_failed = muon_rel_iso > m_muo_iso_max;
        //turn around for iso-inversion
        if( m_muo_invertIso ) iso_failed = !iso_failed;
        //now check
        if( iso_failed ) return 1;
    }
    return 0;
}


bool MuonSelector::passKinematics(pxl::Particle *muon) const {
    //pt cut
    if (muon->getPt() < m_muo_pt_min)
      return false;
    //eta cut
    if (fabs(muon->getEta()) > m_muo_eta_max)
      return false;

    return true;
}


int MuonSelector::muonID(pxl::Particle *muon , double rho) const {
    bool passKin = false;
    bool passID = false;
    bool passIso = false;

    // kinematics check
    passKin = passKinematics(muon);

    //the muon cuts are according to :
    //https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMuonId?rev=49
    //status: 17.9.2014

    // decide which ID should be performed
    if (m_muo_id_type == "CombinedID") {
        if (muon->getPt() < m_muo_ptSwitch) {
            passID = passTightID(muon);
        } else {
            passID = passHighPtID(muon);
        }
    } else if (m_muo_id_type == "HighPtID") {
        passID = passHighPtID(muon);
    } else if (m_muo_id_type == "TightID") {
        passID = passTightID(muon);
    } else if (m_muo_id_type == "MediumID") {
        passID = passMediumID(muon);
    } else if (m_muo_id_type == "SoftID") {
        passID = passSoftID(muon);
    } else {
        throw Tools::config_error("'Muon.ID.Type' must be one of these values: 'CombinedID', 'TightID', 'MediumID', 'SoftID'. The value is '" + m_muo_id_type + "'");
        passID = false;
    }

    // decide which isolation to perform
    if (m_muo_iso_type == "PF") {
        passIso = passPFIso(muon, rho);
    } else if (m_muo_iso_type == "Tracker") {
        passIso = passTrackerIso(muon);
    } else if (m_muo_iso_type == "Mini") {
        passIso = passMiniIso(muon);
    } else {
        throw Tools::config_error("'Muon.Iso.Type' must be one of these values: 'PF', 'Tracker', 'Mini', 'SoftID'. The value is '" + m_muo_iso_type + "'");
        passIso = false;
    }

    // perform iso inversion if requested
    if (m_muo_invertIso) passIso = !passIso;

    // return code depending on passing variables
    if      (passKin  && passID  && passIso)  return 0;
    else if (passKin  && passID  && !passIso) return 1;
    else if (passKin  && !passID && passIso)  return 2;
    else if (!passKin && passID  && passIso)  return 3;
    return 4;
}

bool MuonSelector::passSoftID(pxl::Particle *muon) const {
    // return built-in bool if requested
    if (m_muo_softid_useBool)
        return muon->getUserRecord(m_muo_softid_boolName).toBool();
    // do the cut based ID if we are not using the bool
    if( not muon->getUserRecord("isGoodTMOneST").toBool() )
        return false;
    if( muon->getUserRecord("TrackerLayersWithMeas").toInt32() <= m_muo_softid_trackerLayersWithMeas_min )
        return false;
    if( muon->getUserRecord("PixelLayersWithMeas").toInt32() <= m_muo_softid_pixelLayersWithMeas_min )
        return false;
    if( not muon->getUserRecord("QualityInnerTrack").toBool() )
        return false;
    if( muon->getUserRecord("DxyIT").toDouble() >= m_muo_softid_dxy_max )
        return false;
    if( muon->getUserRecord("DzIT").toDouble() >= m_muo_softid_dz_max )
        return false;
    return true;
}

bool MuonSelector::passMediumID(pxl::Particle *muon) const {
    // return built-in bool if requested
    if (m_muo_mediumid_useBool)
        return muon->getUserRecord(m_muo_mediumid_boolName).toBool();
    // do the cut based ID if we are not using the bool
    if( not muon->getUserRecord("isLooseMuon").toBool() )
        return false;
    if( muon->getUserRecord("validFraction").toDouble() <= m_muo_mediumid_validFraction_min)
        return false;
    // there are two different set of cuts for the medium ID - at least one of them must be true
    // first set:
    // need to start with this set and return true since there is no isValidGlobalTrack variable and thus
    // muon->getUserRecord("normalizedChi2").toDouble() will fail if there is no global track
    // (therefore one has to return from the function if isGlobalMuon is false)
    if( not ( muon->getUserRecord("SegComp").toDouble() <= m_muo_mediumid_segCompTight_min ) )
        return true;
    // second set:
    if( not muon->getUserRecord("isGlobalMuon").toBool() )
        return false;
    if( muon->getUserRecord("normalizedChi2").toDouble() >= m_muo_mediumid_normalizedChi2_max )
        return false;
    if( muon->getUserRecord("chi2LocalPosition").toDouble() >= m_muo_mediumid_chi2LocalPosition_max )
        return false;
    if( muon->getUserRecord("trkKink").toDouble() >= m_muo_mediumid_trkKink_max )
        return false;
    if( muon->getUserRecord("SegComp").toDouble() <= m_muo_mediumid_segCompGlobal_min )
        return false;
    return true;
}

bool MuonSelector::passTightID(pxl::Particle *muon) const {
    // return built-in bool if requested
    if (m_muo_tightid_useBool)
        return muon->getUserRecord(m_muo_tightid_boolName).toBool();
    // do the cut based ID if we are not using the bool
    if( not muon->getUserRecord("isGlobalMuon").toBool() )
        return false;
    if( not muon->getUserRecord("isPFMuon").toBool() )
        return false;
    if( muon->getUserRecord("normalizedChi2").toDouble() >= m_muo_tightid_normalizedChi2_max )
        return false;
    if( muon->getUserRecord("VHitsMuonSys").toInt32() <= m_muo_tightid_vHitsMuonSys_min )
        return false;
    if( muon->getUserRecord("NMatchedStations").toInt32() <= m_muo_tightid_nMatchedStations_min )
        return false;
    if( muon->getUserRecord("Dxy").toDouble() >= m_muo_tightid_dxy_max )
        return false;
    if( muon->getUserRecord("Dz").toDouble() >= m_muo_tightid_dz_max )
        return false;
    if( muon->getUserRecord("VHitsPixel").toInt32() <= m_muo_tightid_vHitsPixel_min )
        return false;
    if( muon->getUserRecord("TrackerLayersWithMeas").toInt32() <= m_muo_tightid_trackerLayersWithMeas_min )
        return false;
    return true;
}

bool MuonSelector::passHighPtID(pxl::Particle *muon) const {
    // check if a cocktail muon exists
    if (!muon->getUserRecord("validCocktail").toBool())
        return false;
    // return built-in bool if requested
    if (m_muo_highptid_useBool)
        return muon->getUserRecord(m_muo_highptid_boolName).toBool();

    // do the cut based ID if we are not using the bool
    if (!(m_muo_highptid_isGlobalMuon == muon->getUserRecord("isGlobalMuon").toBool()))
        return false;
    if (!(m_muo_highptid_ptRelativeError_max > muon->getUserRecord("ptErrorCocktail").toDouble() /
          muon->getUserRecord("ptCocktail").toDouble()))
        return false;

    if (!(m_muo_highptid_nMatchedStations_min < muon->getUserRecord("NMatchedStations").toInt32()))
        return false;
    if (!(m_muo_highptid_vHitsMuonSys_min < muon->getUserRecord("VHitsMuonSysCocktail").toInt32()))
        return false;
    if (!(m_muo_highptid_vHitsPixel_min < muon->getUserRecord("VHitsPixelCocktail").toInt32()))
        return false;
    if (!(m_muo_highptid_vHitsTracker_min < muon->getUserRecord("VHitsTrackerCocktail").toInt32()))
        return false;

    if (!(m_muo_highptid_dxy_max > muon->getUserRecord("DxyCocktail").toDouble()))
        return false;
    if (!(m_muo_highptid_dz_max > muon->getUserRecord("DzCocktail").toDouble()))
        return false;

    // return true if everything passed
    return true;
}


bool MuonSelector::passMiniIso(pxl::Particle *muon) const {
    // TODO(millet) implement mini iso
    return true;
}

bool MuonSelector::passTrackerIso(pxl::Particle *muon) const {
    // TODO(millet) implement mini iso
    double muon_iso = muon->getUserRecord( "TrkIso" );
    return (muon_iso / muon->getPt() < m_muo_iso_max);
}

bool MuonSelector::passPFIso(pxl::Particle *muon, double rho) const {
    // TODO(millet) legacy code, check for 13TeV changes
    double muon_iso;
    // [sumChargedHadronPt+ max(0.,sumNeutralHadronPt+sumPhotonPt-0.5sumPUPt]/pt
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
                       -  rho * (photonEA+neutralHadronEA)
                       );

    } else {
        muon_iso = muon->getUserRecord( "PFIsoR04ChargedHadrons" ).toDouble()
                + muon->getUserRecord( "PFIsoR04NeutralHadrons" ).toDouble()
                + muon->getUserRecord( "PFIsoR04Photons" ).toDouble();
    }

    return (muon_iso / muon->getPt() < m_muo_iso_max);
}
