#include "SampleAnalyzer/Commons/Service/IsolationBase.h"
using namespace MA5;



/// -----------------------------------------------
/// sumPT Lepton vs Tracks
/// -----------------------------------------------
Double_t IsolationBase::sumPT(const RecLeptonFormat* part, 
                              const std::vector<RecTrackFormat>& tracks,
                              const double& DR, 
                              double PTmin) const
{
  double sumPT=0.;
  unsigned int counter=0;

  // Loop over the towers
  for (unsigned int i=0;i<tracks.size();i++)
  {
    const RecTrackFormat& track = tracks[i];

    // Cut on the PT
    if (track.pt()<PTmin) continue;

    // Cut on the DR
    if (part->momentum().DeltaR(track.momentum()) > DR) continue;

    // Cut on id
    if (track.isDelphesUnique(part->delphesTags())) continue;

    // Sum
    sumPT += track.pt();
    counter++;
  }

  // return PT sum of tracks in the cone
  return sumPT;
}


/// -----------------------------------------------
/// sumPT Lepton vs Towers
/// -----------------------------------------------
Double_t IsolationBase::sumPT(const RecLeptonFormat* part, 
                              const std::vector<RecTowerFormat>& towers,
                              const double& DR, 
                              double PTmin) const
{
  double sumPT=0.;
  unsigned int counter=0;

  // Loop over the tracks
  for (unsigned int i=0;i<towers.size();i++)
  {
    const RecTowerFormat& tower = towers[i];

    // Cut on the PT
    if (tower.pt()<PTmin) continue;

    // Cut on the DR
    if (part->momentum().DeltaR(tower.momentum()) > DR) continue;

    // Sum
    sumPT += tower.pt();
    counter++;
  }

  // return PT sum of towers in the cone
  return sumPT;
}


/// -----------------------------------------------
/// sumPT Lepton vs Eflow object
/// -----------------------------------------------
Double_t IsolationBase::sumPT(const RecLeptonFormat* part, 
                              const std::vector<RecParticleFormat>& towers,
                              const double& DR, 
                              double PTmin) const
{
  double sumPT=0.;
  unsigned int counter=0;

  // Loop over the tracks
  for (unsigned int i=0;i<towers.size();i++)
  {
    const RecParticleFormat& tower = towers[i];

    // Cut on the PT
    if (tower.pt()<PTmin) continue;

    // Cut on the DR
    if (part->momentum().DeltaR(tower.momentum()) > DR) continue;

    // Sum
    sumPT += tower.pt();
    counter++;
  }

  // return PT sum of towers in the cone
  return sumPT;
}


/// -----------------------------------------------
/// sumPT Photon vs Tracks
/// -----------------------------------------------
Double_t IsolationBase::sumPT(const RecPhotonFormat* part, 
                              const std::vector<RecTrackFormat>& tracks,
                              const double& DR, 
                              double PTmin) const
{
  double sumPT=0.;
  unsigned int counter=0;

  // Loop over the towers
  for (unsigned int i=0;i<tracks.size();i++)
  {
    const RecTrackFormat& track = tracks[i];

    // Cut on the PT
    if (track.pt()<PTmin) continue;

    // Cut on the DR
    if (part->momentum().DeltaR(track.momentum()) > DR) continue;

    // Sum
    sumPT += track.pt();
    counter++;
  }

  // return PT sum of tracks in the cone
  return sumPT;
}


/// -----------------------------------------------
/// sumPT Photon vs Towers
/// -----------------------------------------------
Double_t IsolationBase::sumPT(const RecPhotonFormat* part, 
                         const std::vector<RecTowerFormat>& towers,
                         const double& DR, 
                         double PTmin) const
{
  double sumPT=0.;
  unsigned int counter=0;

  // Loop over the tracks
  for (unsigned int i=0;i<towers.size();i++)
  {
    const RecTowerFormat& tower = towers[i];

    // Cut on the PT
    if (tower.pt()<PTmin) continue;

    // Cut on the DR
    if (part->momentum().DeltaR(tower.momentum()) > DR) continue;

    // Sum
    sumPT += tower.pt();
    counter++;
  }

  // return PT sum of towers in the cone
  return sumPT;
}


/// -----------------------------------------------
/// sumPT Photon vs Eflow object
/// -----------------------------------------------
Double_t IsolationBase::sumPT(const RecPhotonFormat* part, 
                         const std::vector<RecParticleFormat>& towers,
                         const double& DR, 
                         double PTmin) const
{
  double sumPT=0.;
  unsigned int counter=0;

  // Loop over the tracks
  for (unsigned int i=0;i<towers.size();i++)
  {
    const RecParticleFormat& tower = towers[i];

    // Cut on the PT
    if (tower.pt()<PTmin) continue;

    // Cut on the DR
    if (part->momentum().DeltaR(tower.momentum()) > DR) continue;

    // Cut on id
    if (tower.isDelphesUnique(part->delphesTags())) continue;

    // Sum
    sumPT += tower.pt();
    counter++;
  }

  // return PT sum of towers in the cone
  return sumPT;
}


