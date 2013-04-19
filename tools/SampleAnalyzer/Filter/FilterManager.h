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


#ifndef FILTER_MANAGER_h
#define FILTER_MANAGER_h

// SampleAnalyzer headers
#include "SampleAnalyzer/Filter/FilterBase.h"
#include "SampleAnalyzer/Core/ManagerBase.h"

namespace MA5
{

class FilterManager : public ManagerBase<FilterBase>
{
  // -------------------------------------------------------------
  //                       method members
  // -------------------------------------------------------------
 public :

  /// Constructor without argument
  FilterManager() : ManagerBase<FilterBase>()
  { }

  /// Destructor
  ~FilterManager()
  { }

  /// Let the user selectes an analysis 
  FilterBase* ChoiceFilter();

  /// Build the table
  void BuildTable();
};

}

#endif