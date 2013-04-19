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


// ZIP headers
#ifdef ZIP_USE
   #include "SampleAnalyzer/Core/gz_ostream.h"
#endif

// SampleHeader headers
#include "SampleAnalyzer/Writer/WriterTextBase.h"
#include "SampleAnalyzer/Service/LogService.h"
#include "SampleAnalyzer/Reader/ReaderBase.h"

using namespace MA5;

// -----------------------------------------------------------------------------
// Initialize
// -----------------------------------------------------------------------------
bool WriterTextBase::Initialize(const std::string& rawfilename)
{
  // Is the file stored in Rfio
  rfio_ = ReaderBase::IsRfioMode(rawfilename);

  // Check consistency with compilation option
  if (rfio_)
  {
#ifndef RFIO_USE
    ERROR << "'-rfio' is not allowed. Please set the RFIO_USE"
          << " variable in the Makefile to 1 and recompile the program if"
          << " you would like to use this option." << endmsg;
    exit(1);
#endif
  }

  // Cleaning the file (remove rfio or local location)
  std::string filename = rawfilename;
  ReaderBase::CleanFilename(filename);

  // Is compressed file ?
  compress_ = ReaderBase::IsCompressedMode(filename);

  // Checking consistency with compilation option
  if (compress_)
  {
#ifndef ZIP_USE
    ERROR << "'zip file' is not allowed. Please set the RFIO_USE"
          << " variable in the Makefile to 1 and recompile the program if"
          << " you would like to use this option." << endmsg;
    exit(1);
#endif
  }

  // Creating a tag indicating the file is opened correctlly
  bool test=false;

  // Input coming from RFIO and Compressed
  if (rfio_ && compress_ )
  {
    ERROR << "'zip file' is not allowed. Please set the RFIO_USE"
          << " variable in the Makefile to 1 and recompile the program if"
          << " you would like to use this option." << endmsg;
    exit(1);
  }

  // Input coming from zip archive
  else if (compress_)
  {
#ifdef ZIP_USE
    output_=new gz_ostream();
    gz_ostream * myoutput = dynamic_cast<gz_ostream*>(output_);
    myoutput->open(const_cast<char*>(filename.c_str()));
    test=myoutput->good();
#endif
  }

  // Output coming from local disk
  else 
  {
    output_=new std::ofstream();
    std::ofstream * myoutput = dynamic_cast<std::ofstream*>(output_);
    myoutput->open(filename.c_str());
    test=myoutput->good();
  }

  // Check if the input is properly opened
  if (!test)
  {
    ERROR << "Opening file " << filename 
          << " in write in mode failed" << endmsg;
    exit(1);
  }

  // Return the status
  return test;
}


// -----------------------------------------------------------------------------
// Finalize
// -----------------------------------------------------------------------------
bool WriterTextBase::Finalize()
{
  if (rfio_ && compress_)
  {
    return true;
  }
  else if (compress_)
  {
#ifdef ZIP_USE
    gz_ostream * myoutput = dynamic_cast<gz_ostream*>(output_);
    myoutput->close();
    myoutput->clear();
#endif
  }
  else 
  {
    std::ofstream * myoutput = dynamic_cast<std::ofstream*>(output_);
    myoutput->close();
    myoutput->clear();   
  }

  // Free allocated memory for the file streamer
  if (output_!=0) { delete output_;output_=0; }

  // OK!
  return true;
}
