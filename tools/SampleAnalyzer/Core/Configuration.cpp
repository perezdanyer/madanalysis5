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


// STL headers
#include <algorithm>
#include <fstream>
#include <locale>

// SampleAnalyzer headers
#include "SampleAnalyzer/Core/Configuration.h"
#include "SampleAnalyzer/Service/LogService.h"


using namespace MA5;


// -----------------------------------------------------------------------------
// PrintSyntax
// -----------------------------------------------------------------------------
void Configuration::PrintSyntax()
{
  INFO << endmsg;
  INFO << "Syntax : SampleAnalyzer [option] <filelist>" << endmsg;
  INFO << " with <filelist> = txt file containing all sample file names"
       << endmsg;
  INFO << " with [option] = " << endmsg;
  INFO << "   --check_event      : check the compliance of the event file"
       << endmsg;
  INFO << "   --no_event_weight  : the event weights are not used"
       << endmsg;
  INFO << endmsg;
}


// -----------------------------------------------------------------------------
// Lower
// -----------------------------------------------------------------------------
void Configuration::Lower(std::string& word)
{
  std::transform(word.begin(), word.end(), 
                 word.begin(), 
                 (int (*)(int))std::tolower);
}


// -----------------------------------------------------------------------------
// Initialize
// -----------------------------------------------------------------------------
bool Configuration::Initialize(int &argc, char *argv[])
{
  // Checking number of arguments
  // <filelist> is compulsory
  if (argc<2)
  {
    ERROR << "number of arguments is incorrect." << endmsg;
    PrintSyntax();
    return false;
  }

  // Decoding options
  if (argc>=3) for (unsigned int i=1;i<static_cast<unsigned int>(argc-1);i++)
  {
    // converting const char to string
    std::string option = std::string(argv[i]);
    Lower(option);

    // safety : skip empty string
    if (option.size()==0) continue;

    // check event
    if (option=="--check_event") check_event_ = true;

    // weighted event
    else if (option=="--no_event_weight") no_event_weight_ = true;

    // unknown option
    else
    {
      ERROR << "argument '" << option << "' is unknown !!!" << endmsg;
      PrintSyntax();
      return false;
    }
  }

  // Extracting the input list
  input_list_name_ = std::string(argv[static_cast<unsigned int>(argc-1)]);

  // Ok
  return true;
}


// -----------------------------------------------------------------------------
// Display
// -----------------------------------------------------------------------------
void Configuration::Display()
{
  INFO << "      - general: ";

  // Is there option ?
  if (!check_event_ && !no_event_weight_)
  {
    INFO << "everything is default." << endmsg;
    return;
  }
  else
  {
    INFO << endmsg;
  }

  // Displaying options
  if (check_event_) 
    INFO << "     -> checking the event file format." << endmsg;
  if (no_event_weight_) 
    INFO << "     -> event weights are not used." << endmsg;
}