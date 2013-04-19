////////////////////////////////////////////////////////////////////////////////
//  
//  Copyright (C) 2012 Eric Conte, Benjamin Fuks, Guillaume Serret
//  The MadAnalysis development team, email: <ma5team@iphc.cnrs.fr>
//  
//  This file is part of MadAnalysis 5.
//  Official website: <http://madanalysis.irmp.ucl.ac.be>
//  
//  MadAnalysis 5 is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//  
//  MadAnalysis 5 is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
//  GNU General Public License for more details.
//  
//  You should have received a copy of the GNU General Public License
//  along with MadAnalysis 5. If not, see <http://www.gnu.org/licenses/>
//  
////////////////////////////////////////////////////////////////////////////////


#include "SampleAnalyzer/JetClustering/TauTagger.h"
using namespace MA5;

void TauTagger::Method1 (SampleFormat& mySample, EventFormat& myEvent)
{
  std::vector<RecJetFormat*> Candidates;

  // loop on the particles searching for tau
  for (unsigned int i=0;i<myEvent.mc()->particles().size();i++)
  {
    if (PHYSICS->IsInitialState(myEvent.mc()->particles()[i])) continue;
    if (fabs(myEvent.mc()->particles()[i].pdgid())!=15) continue;

    if (!IsLast(&myEvent.mc()->particles()[i], myEvent)) continue;

    Bool_t tag = false;
    Double_t DeltaRmax = DeltaRmax_;

    // loop on the jets
    for (unsigned int j=0;j<myEvent.rec()->jets().size();j++)
    {
      if (myEvent.rec()->jets()[j].ntracks()!=1 && myEvent.rec()->jets()[j].ntracks()!=3) continue;

      // Calculating Delta R
      Float_t DeltaR = myEvent.mc()->particles()[i].dr(myEvent.rec()->jets()[j]);

      if (DeltaR <= DeltaRmax)
      {
        if(Exclusive_)
        {
          if (tag) Candidates.pop_back();
          tag = true;
          DeltaRmax = DeltaR;
        }
        Candidates.push_back(& myEvent.rec()->jets()[j]);
      }
    }

    sort(Candidates.begin(),Candidates.end());

    for (unsigned int j=Candidates.size();j>0;j--)
    {
      Candidates[j-1]->mc_ = &myEvent.mc()->particles()[i];
      RecTauFormat* myTau = myEvent.rec()->GetNewTau();
      Jet2Tau(Candidates[j-1], myTau, myEvent);
      myEvent.rec()->jets().erase((std::vector<RecJetFormat>::iterator) Candidates[j-1]);
    }

    Candidates.clear();
  }
}

void TauTagger::Method2 (SampleFormat& mySample, EventFormat& myEvent)
{
  std::vector<RecJetFormat*> Candidates;

  for (unsigned int i=0;i<myEvent.rec()->jets().size();i++)
  {
    if (myEvent.rec()->jets()[i].ntracks()!=1 && myEvent.rec()->jets()[i].ntracks()!=3) continue;

    Bool_t tag = false;
    // Loop on the jets constituents
    for (unsigned int j=0;j<myEvent.rec()->jets()[i].Constituents_.size();j++)
    {
      // Searching for a tau in the history
      Int_t N = myEvent.rec()->jets()[i].Constituents_[j];
      MCParticleFormat* particle = & myEvent.mc()->particles()[N];
      while (!tag)
      {
       	if (particle==0)
        {
          ERROR << "No particle" << endmsg;
          break;
        }
	if (particle->statuscode()==3) break;

        if (fabs(particle->pdgid())==15)
        {
          tag = true;
          myEvent.rec()->jets()[i].mc_ = particle;
          break;
        }

	if (particle->mother2()!=0 && particle->mother2()!=particle->mother1()) break;

        particle = particle->mother1();
      }

      if (tag) break;
    }

    if (tag) Candidates.push_back(& myEvent.rec()->jets()[i]);
  }

  if (Exclusive_)
  {
    UInt_t i = 0;
    UInt_t n = Candidates.size();

    while (i<n)
    {
      UInt_t j = i+1;

      Float_t DeltaR = Candidates[i]->mc()->dr(Candidates[i]);

      while (j<n)
      {
        // If two candidates are matching with the same tau, erasing the one with the greater Delta R and reducing n (the size of the vector)
       	if (Candidates[i]->mc()==Candidates[j]->mc())
        {
          Float_t DeltaR2 = Candidates[j]->mc()->dr(Candidates[j]);

          if (DeltaR2<DeltaR) std::swap(Candidates[i], Candidates[j]);

          Candidates.erase(Candidates.begin()+j);
          n--;
	}
	else j++;
      }

      i++;
    }
  }

  sort(Candidates.begin(),Candidates.end());

  for (unsigned int i=Candidates.size();i>0;i--)
  {
    RecTauFormat* myTau = myEvent.rec()->GetNewTau();
    Jet2Tau(Candidates[i-1], myTau, myEvent);
    myEvent.rec()->jets().erase((std::vector<RecJetFormat>::iterator) Candidates[i-1]);
  }
  Candidates.clear();
}

void TauTagger::Method3 (SampleFormat& mySample, EventFormat& myEvent)
{
  std::vector<RecJetFormat*> Candidates;

  // Jets preselection using method 2
  for (unsigned int i=0;i<myEvent.rec()->jets().size();i++)
  {
    if (myEvent.rec()->jets()[i].ntracks()!=1 && myEvent.rec()->jets()[i].ntracks()!=3) continue;

    Bool_t tag = false;
    for (unsigned int j=0;j<myEvent.rec()->jets()[i].Constituents_.size();j++)
    {
      Int_t N = myEvent.rec()->jets()[i].Constituents_[j];
      MCParticleFormat* particle = & myEvent.mc()->particles()[N];
      while (!tag)
      {
       	if (particle==0)
        {
          ERROR << "No particle" << endmsg;
          break;
        }

        if (particle->statuscode()==3) break;

        if (fabs(particle->pdgid())==15)
        {
          tag = true;
          myEvent.rec()->jets()[i].mc_ = particle;
          break;
        }

	if (particle->mother2()!=0 && particle->mother2()!=particle->mother1()) break;

        particle = particle->mother1();
      }

      if (tag) break;
    }

    if (tag) Candidates.push_back(& myEvent.rec()->jets()[i]);
  }

  std::vector<RecJetFormat*> Taus;

  // tau-tagging using method 1
  for (unsigned int i=0;i<myEvent.mc()->particles().size();i++)
  {
    if (fabs(myEvent.mc()->particles()[i].pdgid())!=15) continue;

    if (!IsLast(&myEvent.mc()->particles()[i], myEvent)) continue;

    Double_t DeltaRmax = DeltaRmax_; 
    Bool_t tag = false;

    for (unsigned int j=Candidates.size();j>0;j--)
    {
      Float_t DeltaR = myEvent.mc()->particles()[i].dr(Candidates[j-1]);

      if (DeltaR <= DeltaRmax)
      {
        if (Exclusive_)
        {
          if (tag) Taus.pop_back();
          tag = true;
          DeltaRmax = DeltaR;
        }
     	Taus.push_back(Candidates[j-1]);
	Candidates.erase(Candidates.begin()+j-1);
      }
    }
  }

  sort(Taus.begin(),Taus.end());

  for (unsigned int j=Taus.size();j>0;j--)
  {
    RecTauFormat* myTau = myEvent.rec()->GetNewTau();
    Jet2Tau(Taus[j-1], myTau, myEvent);
    myEvent.rec()->jets().erase((std::vector<RecJetFormat>::iterator) Taus[j-1]);
  }

  Taus.clear();
  Candidates.clear();
}

void TauTagger::Jet2Tau (RecJetFormat* myJet, RecTauFormat* myTau, EventFormat& myEvent)
{
  myTau->setMomentum(myJet->momentum());
  myTau->ntracks_ = myJet->ntracks();
  myTau->mc_ = myJet->mc_;
  myTau->DecayMode_ = PHYSICS->GetTauDecayMode(myTau->mc_);

  Int_t charge = 0;

  for (unsigned int i=0;i<myJet->Constituents_.size();i++)
  {
    charge += PDG->GetCharge(myEvent.mc()->particles()[myJet->Constituents_[i]].pdgid());
  }

  if (charge == 3) myTau->charge_ = true;
  else if (charge == -3) myTau->charge_ = false;
}