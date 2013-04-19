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


#ifndef JETCLUSTERINGGRIDJET_H
#define JETCLUSTERINGGRIDJET_H

#ifdef FASTJET_USE

//SampleAnalyser headers
#include "SampleAnalyzer/JetClustering/JetClusteringPlugin.h"

//FastJet headers
#include <fastjet/GridJetPlugin.hh>

namespace MA5
{

class JetClusteringGridJet: public JetClusteringPlugin
{
//---------------------------------------------------------------------------------
//                                 data members
//---------------------------------------------------------------------------------
  private :

    /// y max
    Double_t Ymax_;

    /// Requested Grid Spacing in y and phi
    Double_t RequestedGridSpacing_;

//---------------------------------------------------------------------------------
//                                method members
//---------------------------------------------------------------------------------
  public :

    /// Constructor without argument
    JetClusteringGridJet() {Ymax_=2.5; RequestedGridSpacing_=0.05;}

    /// Destructor
    virtual ~JetClusteringGridJet () {}

    /// Initialization
    virtual bool Initialize(const std::map<std::string,std::string>& options);

    /// Print parameters
    virtual void PrintParam ();

    /// Accessor to the jet clusterer name
    virtual std::string GetName();

    /// Accessor to the jet clusterer parameters
    virtual std::string GetParameters();

};

}

#endif
#endif