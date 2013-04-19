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


#ifndef ANALYSISBASE_h
#define ANALYSISBASE_h

// SampleAnalyzer headers
#include "SampleAnalyzer/DataFormat/EventFormat.h"
#include "SampleAnalyzer/DataFormat/SampleFormat.h"
#include "SampleAnalyzer/Plot/PlotManager.h"
#include "SampleAnalyzer/Counter/CounterManager.h"
#include "SampleAnalyzer/Writer/SAFWriter.h"
#include "SampleAnalyzer/Service/Physics.h"
#include "SampleAnalyzer/Service/LogService.h"
#include "SampleAnalyzer/Core/Configuration.h"

// STL headers
#include <set>
#include <string>
#include <cmath>

// ROOT headers
#include <TTree.h>
#include <TStyle.h>
#include <TLine.h>
#include <TLegend.h>
#include <TFile.h>
#include <TROOT.h>
#include <Rtypes.h>
#include <TCanvas.h>
#include <TH1F.h>
#include <TVector.h>
#include <TClonesArray.h>


// initializing MACRO 
#define INIT_ANALYSIS(CLASS,NAME) public: CLASS() {setName(NAME);} virtual ~CLASS() {} private:

namespace MA5
{

class AnalyzerBase
{

  // -------------------------------------------------------------
  //                        data members
  // -------------------------------------------------------------
 public :

  /// name of the analysis
  std::string name_;

  /// Weighted events mode
  bool weighted_events_;

  /// Writer SAF
  SAFWriter out_;


  // -------------------------------------------------------------
  //                       method members
  // -------------------------------------------------------------
 public :

  /// Constructor without argument 
  AnalyzerBase()
  { name_="unknown"; }

  /// Destructor
  virtual ~AnalyzerBase()
  { }

  /// Initialize (common part to all analyses)
  bool PreInitialize(const std::string& outputName, 
                     bool weighted_events=false)
  {
    weighted_events_ = weighted_events;
    out_.Initialize(outputName.c_str());
    return true;
  }

  /// Initialize (specific to the analysis)
  virtual bool Initialize(const Configuration& cfg)=0;

  /// PreFinalize
  void PreFinalize(const SampleFormat& summary, 
                   const std::vector<SampleFormat>& samples)
  { 
    out_.WriteHeader(summary); 
    out_.WriteFiles(samples);
  }

  /// Finalize
  virtual void Finalize(const SampleFormat& summary, 
                        const std::vector<SampleFormat>& samples)=0;

  /// PostFinalize
  void PostFinalize(const SampleFormat& summary,
                    const std::vector<SampleFormat>& samples)
  {
    // Closing output file
    out_.WriteFoot(summary);
    out_.Finalize();
  }

  /// Execute
  void PreExecute(const SampleFormat& mySample,
                  const EventFormat& myEvent)
  { 
    PHYSICS->SetFinalState(myEvent.mc());
    PHYSICS->SetInitialState(myEvent.mc());
  }

  virtual void Execute(SampleFormat& mySample,
                       const EventFormat& myEvent)=0;

  /// Accessor to analysis name
  const std::string name() const {return name_;}

  /// Mutator to analysis name
  void setName(const std::string& Name) {name_=Name;}

  SAFWriter& out()
  { return out_; }


 protected :

};

}


#endif