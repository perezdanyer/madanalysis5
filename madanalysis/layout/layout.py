################################################################################
#  
#  Copyright (C) 2012-2020 Jack Araz, Eric Conte & Benjamin Fuks
#  The MadAnalysis development team, email: <ma5team@iphc.cnrs.fr>
#  
#  This file is part of MadAnalysis 5.
#  Official website: <https://launchpad.net/madanalysis5>
#  
#  MadAnalysis 5 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  MadAnalysis 5 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with MadAnalysis 5. If not, see <http://www.gnu.org/licenses/>
#  
################################################################################


from __future__ import absolute_import
from madanalysis.enumeration.sb_ratio_type             import SBratioType
from madanalysis.enumeration.color_type                import ColorType
from madanalysis.enumeration.cut_type                  import CutType
from madanalysis.enumeration.report_format_type        import ReportFormatType
from madanalysis.enumeration.normalize_type            import NormalizeType
from madanalysis.enumeration.observable_type           import ObservableType
from madanalysis.enumeration.graphic_render_type       import GraphicRenderType
from madanalysis.enumeration.font_type                 import FontType
from madanalysis.enumeration.script_type               import ScriptType
from madanalysis.IOinterface.folder_writer             import FolderWriter
from madanalysis.IOinterface.text_report               import TextReport
from madanalysis.IOinterface.html_report_writer        import HTMLReportWriter
from madanalysis.IOinterface.latex_report_writer       import LATEXReportWriter
from madanalysis.IOinterface.histo_root_producer       import HistoRootProducer
from madanalysis.IOinterface.histo_matplotlib_producer import HistoMatplotlibProducer
from madanalysis.layout.cutflow                        import CutFlow
from madanalysis.layout.plotflow                       import PlotFlow
from madanalysis.layout.merging_plots                  import MergingPlots
from madanalysis.selection.instance_name               import InstanceName
from math                                              import log10, floor, ceil, isnan, isinf
import os
import shutil
import logging
from six.moves import range

class Layout:

    def __init__(self,main):
        self.main         = main
        self.input_path   = self.main.lastjob_name
        self.cutflow      = CutFlow(self.main)
        self.plotflow     = PlotFlow(self.main)
        self.merging      = MergingPlots(self.main)
        self.logger       = logging.getLogger('MA5')

    def Initialize(self):

        # Calculating cut efficiencies
        self.cutflow.Initialize()

        # Creating histograms
        self.plotflow.Initialize()
        self.merging.Initialize()

    @staticmethod
    def DisplayInteger(value):
        if type(value) is not int:
            return ""
        if value<0:
            return "-" + Layout.DisplayInteger(-value)
        elif value < 1000:
            return str(value)
        else:
            return Layout.DisplayInteger(value / 1000) +\
                   "," + '%03d' % (value % 1000)


    @staticmethod
    def Round_to_Ndigits(x,N):
        # Safety 1
        if N<1:
            return ""
        
        # Safety 2
        if isnan(x):
            return "nan"
        elif isinf(x):
            return "inf"

        # Convert
        if x<(10**(N-1)):
            convert = '%.'+str(N)+'G'
            return '%s' % float(convert % x)
        else:
            tmp = '%s' % float('%.12G' % int(x))
            if len(tmp)>=3 and tmp.endswith('.0'):
                tmp = tmp[:-2]
            return tmp    


    @staticmethod
    def DisplayXsection(xsection,xerror):
        # xsection and xerror are null
        if xsection==0. and xerror==0.:
            return "0.0 @ 0.0%"
            
        # xsection is not null but xerror is
        # keep the 3 significative digit
        elif xerror==0:
            return Layout.Round_to_Ndigits(xsection,3)
        
        # error greater than xsection ? 
        else:
            string1 = Layout.Round_to_Ndigits(xsection,3)
            if xsection ==0.:
              string2="0.0"
            else:
              string2 = Layout.Round_to_Ndigits(100.*xerror/xsection,2)
            return string1 + " @ " + string2 + '%'


    @staticmethod
    def DisplayXsecCut(xsection,xerror):
        # xsection and xerror are null
        if xsection==0. and xerror==0.:
            return "0.0 +/- 0.0"
            
        # xsection is not null but xerror is
        # keep the 3 significative digit
        elif xerror==0:
            return Layout.Round_to_Ndigits(xsection,3)
        
        # error greater than xsection ? 
        elif xsection > xerror:
            string1 = Layout.Round_to_Ndigits(xerror,3)
            if 'e' in string1 or 'E' in string1:
                string2='%.2e' % xsection
                string1='%.2e' % xerror
            elif '.' in string1:
                convert='%.'+str(len(string1.split('.')[1]))+'f'
                string2=convert % xsection
            else:
                string2=str(int(xsection))
            return string2 + " +/- " + string1    

        else:
            string1 = Layout.Round_to_Ndigits(xsection,3)
            if 'e' in string1 or 'E' in string1:
                string2='%.2e' % xerror
                string1='%.2e' % xsection
            elif '.' in string1:
                convert='%.'+str(len(string1.split('.')[1]))+'f'
                string2=convert % xerror
            else:
                string2=str(int(xerror))
            return string1 + " +/- " + string2



    def DoPlots(self,histo_path,modes,output_paths):

        ListPlots = []
        
        # Header plots
        self.logger.debug('Producing scripts for header plots ...')
        if self.main.merging.enable:
            self.merging.DrawAll(histo_path,modes,output_paths,ListPlots)

        # Selection plots
        self.logger.debug('Producing scripts for selection plots ...')
        if self.main.selection.Nhistos!=0:
            self.plotflow.DrawAll(histo_path,modes,output_paths,ListPlots)

        # Foot plots
        self.logger.debug('Producing scripts for foot plots ...')
        # to do

        # Launching ROOT
        if self.main.graphic_render==GraphicRenderType.ROOT:
            producer=HistoRootProducer(histo_path,ListPlots)
            producer.Execute()
        elif self.main.graphic_render==GraphicRenderType.MATPLOTLIB:
            producer=HistoMatplotlibProducer(histo_path,ListPlots)
            producer.Execute()

        # Ok
        return True


    def CopyLogo(self,mode,output_path):
        
        # Filename
        filename = self.main.archi_info.ma5dir+"/madanalysis/input/" + \
                   "logo." + \
                   ReportFormatType.convert2filetype(mode)

        # Checking file presence
        if not os.path.isfile(filename):
            self.logger.error("the image '" + \
                          filename + \
                          "' is not found.")
            return False

        # Copy file
        try :
            shutil.copy(filename,output_path)
            return True
        except:
            self.logger.error("Errors have occured during the copy of the file ")
            self.logger.error(" "+filename)
            return False

    def WriteDatasetTable(self,report,dataset):

        # Datatype
        datatype="signal"
        if dataset.background:
            datatype="background"

        report.OpenBullet()
        text=TextReport()

        # Must we specify the sample folder ?
        specify=False
        for ind in range(0,len(dataset.filenames)):
            samplename = dataset.filenames[ind].replace(self.main.currentdir,'')
            if samplename[0]!='/' or samplename==dataset.filenames[ind]:
                specify=True
                break

        # Displaying the folder
        if specify:
            text.Add('Samples stored in the directory: ')
            text.SetColor(ColorType.BLUE)
            text.Add(self.main.currentdir)
            text.SetColor(ColorType.BLACK)
            text.Add('.\n')
            report.WriteText(text)
            text.Reset()

        # Signal or background sample
        text.Add('Sample consisting of: ')
        text.SetColor(ColorType.BLUE)
        text.Add(datatype)
        text.SetColor(ColorType.BLACK)
        text.Add(' events.\n')
        report.WriteText(text)
        text.Reset()
 
        # Number of generated events
        text.Add('Generated events: ')
        text.SetColor(ColorType.BLUE)
        ngen = int(dataset.measured_global.nevents);
        text.Add(str(ngen) + " ")
        text.SetColor(ColorType.BLACK)
        text.Add(' events.\n')
        report.WriteText(text)
        text.Reset()

        # Cross section imposed by the user
        if dataset.xsection != 0.0:
            text.Add('Cross section imposed by the user: ')
            text.SetColor(ColorType.BLUE)
            text.Add(str(dataset.xsection))
            text.SetColor(ColorType.BLACK)
            text.Add(' pb.\n')
            report.WriteText(text)
            text.Reset()

        # Weight of the events, if different from one
        if dataset.weight != 1.0:
            text.Add('Event weight imposed by the user: ')
            text.SetColor(ColorType.BLUE)
            text.Add(str(dataset.weight))
            text.SetColor(ColorType.BLACK)
            text.Add('.\n')
            report.WriteText(text)
            text.Reset()

        # Number of events after normalization, with the error
        text.Add('Normalization to the luminosity: ')
        text.SetColor(ColorType.BLUE)
        if dataset.xsection != 0.0:
            nlumi = int(dataset.xsection * 1000 * self.main.lumi)
        else:
            nlumi = int(dataset.measured_global.xsection * \
                        1000*self.main.lumi * \
                        dataset.weight)
        text.Add(str(nlumi))
        text.Add(' +/- ')
        if dataset.xsection != 0.0:
            elumi = 0.0
        else:
            elumi = ceil(dataset.measured_global.xerror * 1000 * \
                         self.main.lumi * dataset.weight)
        text.Add(str(int(elumi))+ " ")
        text.SetColor(ColorType.BLACK)
        text.Add(' events.\n')
        report.WriteText(text)
        text.Reset()

        # Statistical significance of the sample
        evw = 0.
        if ngen!=0:
            evw = float(nlumi)/float(ngen)*dataset.weight
           
        if evw > 1:
            text.SetColor(ColorType.RED)
        text.Add('Ratio (event weight): ')
        if evw < 1:
            text.SetColor(ColorType.BLUE)
        text.Add(str(Layout.Round_to_Ndigits(evw,2)) + " ")
        if evw < 1:
            text.SetColor(ColorType.BLACK)
            text.Add('.')
        if evw > 1:
            text.Add(' - warning: please generate more events (weight larger than 1)!\n')
            text.SetColor(ColorType.BLACK)
        else:
            text.Add(' \n')
        report.WriteText(text)
        text.Reset()
        report.CloseBullet()       


        # table with information
        # titles of the columns
        report.CreateTable([6.5,3,3.5,3.5],text)
        report.NewCell(ColorType.YELLOW)
        if len(dataset.filenames)>=2:
            text.Add("        Paths to the event files")
        else:
            text.Add("        Path to the event file")
        report.WriteText(text)
        text.Reset()
        report.NewCell(ColorType.YELLOW)
        text.Add("        Nr. of events")
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        Cross section (pb)")
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        Negative wgts (%)")
        report.WriteText(text)
        text.Reset()
        report.NewLine()

        # information
        for ind in range(0,len(dataset.filenames)):
            color = ColorType.BLACK

            # path to the file
            report.NewCell()
            text.Add('        ')
            text.SetColor(color)
            samplename = str(dataset.filenames[ind]).replace(self.main.currentdir,'')
            if samplename[0]=='/' and samplename!=dataset.filenames[ind]:
                samplename = samplename[1:]
            text.Add(samplename)
            report.WriteText(text)
            text.Reset()

            # number of events
            report.NewCell()
            text.Add('        ')
            text.SetColor(color)
            text.Add(str(int(dataset.measured_detail[ind].nevents)))
            report.WriteText(text)
            text.Reset()

            # cross section
            report.NewCell()
            text.Add('        ')
            text.SetColor(color)
            if dataset.xsection != 0.0:
                text.Add(str(dataset.xsection))
            else:
                value = dataset.measured_detail[ind].xsection * dataset.weight
                error = dataset.measured_detail[ind].xerror * dataset.weight
                text.Add(Layout.DisplayXsection(value,error))
            report.WriteText(text)
            text.Reset()

            # Negative weigths
            report.NewCell()
            text.Add('        ')
            text.SetColor(color)
            if (dataset.measured_detail[ind].sumw_positive +\
                dataset.measured_detail[ind].sumw_negative)==0:
                text.Add(str(0.0))
            else:
                text.Add(Layout.Round_to_Ndigits( 100 * \
                          dataset.measured_detail[ind].sumw_negative / \
                          (dataset.measured_detail[ind].sumw_positive + \
                           dataset.measured_detail[ind].sumw_negative),2 ))
            report.WriteText(text)
            text.Reset()

            # end of the line
            if len(dataset.filenames)==1:
               report.EndLine()
            else:
               report.NewLine()

        # sum if many datasets
        if len(dataset.filenames)!=1:
          color = ColorType.BLUE
          report.NewCell()
          text.Add('        ')
          text.SetColor(color)
          text.Add("Sum")
          report.WriteText(text)
          text.Reset()

          # number of events
          report.NewCell()
          text.Add('        ')
          text.SetColor(color)
          text.Add(str(int(dataset.measured_global.nevents)))
          report.WriteText(text)
          text.Reset()

          # cross section
          report.NewCell()
          text.Add('        ')
          text.SetColor(color)
          if dataset.xsection != 0.0:
              text.Add(str(dataset.xsection))
          else:
              value = dataset.measured_global.xsection * dataset.weight
              error = dataset.measured_global.xerror * dataset.weight
              text.Add(Layout.DisplayXsection(value,error))
          report.WriteText(text)
          text.Reset()

          # Negative weigths
          report.NewCell()
          text.Add('        ')
          text.SetColor(color)
          if (dataset.measured_detail[ind].sumw_positive +\
              dataset.measured_detail[ind].sumw_negative)==0:
              text.Add(str(0.0))
          else:
              text.Add(Layout.Round_to_Ndigits( 100 * \
                        dataset.measured_global.sumw_negative / \
                        (dataset.measured_global.sumw_positive + \
                         dataset.measured_global.sumw_negative),2 ))
          report.WriteText(text)
          text.Reset()

          ## The end of line
          report.EndLine()

        report.EndTable()    
        text.Reset()

    # Writing Final Table
    def WriteFinalTable(self,report,cutinfo):
        # Information
        report.OpenBullet()
        text=TextReport()
        text.Reset()
        text.Add("How to compare signal (S) and background (B): ")
        text.SetColor(ColorType.BLUE)
        text.Add(self.main.fom.getFormula())
        text.SetColor(ColorType.BLACK)
        text.Add('.\n')
        report.WriteText(text)
        text.Reset()
#       text.Add("Associated uncertainty: ")
#       text.SetColor(ColorType.BLUE)
#       text.Add(self.main.SBerror)
#       text.SetColor(ColorType.BLACK)
#       text.Add('.\n')
#       report.WriteText(text)
#       text.Reset()
        text.Add("Object definition selections are indicated in cyan.")
        report.WriteText(text)
        text.Reset()
        text.Add("Reject and select are indicated by 'REJ' and 'SEL' respectively")
        report.WriteText(text)
        text.Reset()
        report.CloseBullet()

        myregs = self.main.regions.GetNames()
        noreg = False
        if myregs==[]:
            myregs = ["myregion"]
            noreg = True
        for reg in myregs:
            # Getting the cutflow names
            reg_cflow  = [ x[0] for x in cutinfo if reg in x[1]]
            type_cflow = [ x[2] for x in cutinfo if reg in x[1]]
            # Printing the table
            report.CreateTable([3.25,3.25,3.25,3.00],text)
            if not noreg:
                report.NewCell(ColorType.GREY,span=4)
                text.Reset()
                text.SetColor(ColorType.WHITE)
                text.Add("Region: \"" + reg + '\"')
                report.WriteText(text)
                text.Reset()
                report.NewLine()
            report.NewCell(ColorType.YELLOW)
            text.Reset()
            text.Add("        Cuts")
            report.WriteText(text)
            report.NewCell(ColorType.YELLOW)
            text.Reset()
            text.Add("        Signal (S)")
            report.WriteText(text)
            report.NewCell(ColorType.YELLOW)
            text.Reset()
            text.Add("        Background (B)")# (+/- err)")
            report.WriteText(text)
            report.NewCell(ColorType.YELLOW)
            text.Reset()
            text.Add("        S vs B")
            report.WriteText(text)
            report.NewLine()
            text.Reset()
            # Initial
            report.NewCell()
            text.Reset()
            text.Add("        Initial (no cut)")
            report.WriteText(text)
            report.NewCell()
            text.Reset()
            if self.cutflow.isSignal:
                text.Add("        " +\
                   Layout.DisplayXsecCut(self.cutflow.signal.Ntotal.mean,
                                               self.cutflow.signal.Ntotal.error))
            else:
                text.Add("        ")
            report.WriteText(text)
            report.NewCell()
            text.Reset()
            if self.cutflow.isBackground:
                text.Add("        " +\
                       Layout.DisplayXsecCut(self.cutflow.background.Ntotal.mean,\
                                             self.cutflow.background.Ntotal.error))
            else:
                text.Add("        ")
            report.WriteText(text)
            report.NewCell()
            text.Reset()
            if self.cutflow.isSignal and self.cutflow.isBackground:
                value = self.cutflow.calculateBSratio(\
                    self.cutflow.background.Ntotal.mean,\
                    self.cutflow.background.Ntotal.error,\
                    self.cutflow.signal.Ntotal.mean,\
                    self.cutflow.signal.Ntotal.error)
                text.Add("        " + Layout.DisplayXsecCut(value.mean,value.error))
            else:
                text.Add("        ")
            report.WriteText(text)
            # Loop
            id_flow=0
            for myflow in self.cutflow.detail[0].cuts:
                if len(myflow)==0:
                    id_flow+=1
                    continue
                if len(myflow[0].cutregion)!=1:
                    self.logger.error('Problem with the interpretation of the output')
                    return False
                if reg in myflow[0].cutregion:
                    break
                id_flow+=1
            if id_flow == len(self.cutflow.detail[0].cuts):
                report.EndLine()
                report.EndTable()
                text.Reset()
                continue
            report.NewLine()
            text.Reset()
            iregf=0
            for ind in range(0,len(self.cutflow.detail[0].Nselected[id_flow])):
                if not self.cutflow.detail[0].cuts[id_flow][ind].cutname[(self.cutflow.detail[0].cuts[id_flow][ind].cutname.find('_')+1):-1] in reg_cflow[iregf]:
                    report.NewCell(ColorType.CYAN)
                    text.Reset()
                    if 'select' in reg_cflow[iregf]:
                        text.Add('SEL: '+ reg_cflow[iregf].strip()[14:][:45])
                    else:
                        text.Add('REJ: '+ reg_cflow[iregf].strip()[14:][:45])
                    report.WriteText(text)
                    report.NewCell(ColorType.CYAN)
                    text.Reset()
                    text.Add("   -   ")
                    report.WriteText(text)
                    report.NewCell(ColorType.CYAN)
                    text.Reset()
                    text.Add("   -   ")
                    report.WriteText(text)
                    report.NewCell(ColorType.CYAN)
                    text.Reset()
                    text.Add("   -   ")
                    report.WriteText(text)
                    report.NewLine()
                    text.Reset()
                    iregf+=1
                iregf+=1
                report.NewCell()
                text.Reset()
                if type_cflow[iregf-1]==CutType.SELECT:
                    text.Add('SEL: ' + self.cutflow.detail[0].cuts[id_flow][ind].cutname[3:-1][:45])
                else:
                    text.Add('REJ: ' + self.cutflow.detail[0].cuts[id_flow][ind].cutname[3:-1][:45])
                report.WriteText(text)
                report.NewCell()
                text.Reset()
                if self.cutflow.isSignal:
                    text.Add("        " + \
                             Layout.DisplayXsecCut(\
                                 self.cutflow.signal.Nselected[id_flow][ind].mean,\
                                 self.cutflow.signal.Nselected[id_flow][ind].error) )
                else:
                    text.Add("        ")
                report.WriteText(text)
                report.NewCell()
                text.Reset()
                if self.cutflow.isBackground:
                    text.Add("        " + \
                             Layout.DisplayXsecCut(\
                                self.cutflow.background.Nselected[id_flow][ind].mean,\
                                self.cutflow.background.Nselected[id_flow][ind].error) )
                else:
                    text.Add("        ")
                report.WriteText(text)
                report.NewCell()
                text.Reset()
                if self.cutflow.isSignal and self.cutflow.isBackground:
                    value = self.cutflow.calculateBSratio(\
                        self.cutflow.background.Nselected[id_flow][ind].mean,\
                        self.cutflow.background.Nselected[id_flow][ind].error,\
                        self.cutflow.signal.Nselected[id_flow][ind].mean,\
                        self.cutflow.signal.Nselected[id_flow][ind].error)
                    text.Add("        " + Layout.DisplayXsecCut(value.mean,value.error))
                else:
                    text.Add("        ")
                report.WriteText(text)
                if ind == (len(self.cutflow.detail[0].Nselected[id_flow])-1) and iregf==len(reg_cflow):
                    report.EndLine()
                else:
                    report.NewLine()
                text.Reset()
            for cand in range(iregf,len(reg_cflow)):
                report.NewCell(ColorType.CYAN)
                text.Reset()
                if 'select' in reg_cflow[cand]:
                    text.Add('SEL: '+ reg_cflow[cand].strip()[14:][:45])
                else:
                    text.Add('REJ: '+ reg_cflow[cand].strip()[14:][:45])
                report.WriteText(text)
                report.NewCell(ColorType.CYAN)
                text.Reset()
                text.Add("   -   ")
                report.WriteText(text)
                report.NewCell(ColorType.CYAN)
                text.Reset()
                text.Add("   -   ")
                report.WriteText(text)
                report.NewCell(ColorType.CYAN)
                text.Reset()
                text.Add("   -   ")
                report.WriteText(text)
                if cand == len(reg_cflow)-1:
                    report.EndLine()
                else:
                    report.NewLine()
                text.Reset()
            report.EndTable()

    # Writing Efficiency Table
    def WriteEfficiencyTable(self,index,icut,report):
        warning_test = False
        text=TextReport()
        myregs = self.main.selection[index].regions
        noreg = False
        if myregs==[]:
            myregs = ["myregion"]
            noreg = True
        for reg in myregs:
            text.Reset()
            report.CreateTable([2.1,2.8,2.8,3.4,3.3],text)
            if not noreg:
                report.NewCell(ColorType.GREY,span=5)
                text.Reset()
                text.SetColor(ColorType.WHITE)
                text.Add("Region: \"" + reg + '\"')
                report.WriteText(text)
                text.Reset()
                report.NewLine()
            report.NewCell(ColorType.YELLOW)
            text.Reset()
            text.Add("        Dataset")
            report.WriteText(text)
            report.NewCell(ColorType.YELLOW)
            text.Reset()
            text.Add("        Events kept:\n")
            text.Add("        K")
            report.WriteText(text)
            report.NewCell(ColorType.YELLOW)
            text.Reset()
            text.Add("        Rejected events:\n")
            text.Add("        R")
            report.WriteText(text)
            report.NewCell(ColorType.YELLOW)
            text.Reset()
            text.Add("        Efficiency:\n")
            text.Add("        K / (K + R)")
            report.WriteText(text)
            report.NewCell(ColorType.YELLOW)
            text.Reset()
            text.Add("        Cumul. efficiency:\n")
            text.Add("        K / Initial")
            report.WriteText(text)
            text.Reset()
            report.NewLine()
            warnings = []
            for i in range(0,len(self.main.datasets)):
                # DatasetName
                report.NewCell()
                text.Reset()
                text.Add('        '+self.main.datasets[i].name)
                report.WriteText(text)
                # get the right region (and thus the right cutflow)
                id_flow=0
                for myflow in self.cutflow.detail[i].cuts:
                    if len(myflow)==0:
                        id_flow+=1
                        continue
                    if len(myflow[0].cutregion)!=1:
                        self.logger.error('Problem with the interpretation of the output')
                        return False
                    if reg in myflow[0].cutregion:
                        break
                    id_flow+=1
                # getting the right cut in the cutflow
                id_cut=0
                for running_cut in self.cutflow.detail[i].cuts[id_flow]:
                    if running_cut.cutname.startswith('\"'+str(icut+1)+'_'):
                        break
                    id_cut+=1
                # SelectedEvents
                report.NewCell()
                text.Reset()
                text.Add('        ' + Layout.DisplayXsecCut(self.cutflow.detail[i].Nselected[id_flow][id_cut].mean,\
                   self.cutflow.detail[i].Nselected[id_flow][id_cut].error))
                report.WriteText(text)
                # RejectedEvents
                report.NewCell()
                text.Reset()
                text.Add('        ' + Layout.DisplayXsecCut(self.cutflow.detail[i].Nrejected[id_flow][id_cut].mean,\
                   self.cutflow.detail[i].Nrejected[id_flow][id_cut].error))
                report.WriteText(text)
                # Efficiency Events
                report.NewCell()
                text.Reset()
                text.Add('        ' + Layout.DisplayXsecCut(self.cutflow.detail[i].eff[id_flow][id_cut].mean,\
                   self.cutflow.detail[i].eff[id_flow][id_cut].error))
                report.WriteText(text)
                # Cumulative efficiency events
                report.NewCell()
                text.Reset()
                text.Add('        ' + Layout.DisplayXsecCut(self.cutflow.detail[i].effcumu[id_flow][id_cut].mean,\
                   self.cutflow.detail[i].effcumu[id_flow][id_cut].error))
                report.WriteText(text)
                if i == (len(self.main.datasets)-1):
                    report.EndLine()
                else:
                    report.NewLine()
                # warnings ?
                if len(self.cutflow.detail[i].warnings[id_flow][id_cut])!=0:
                    warning_test=True
                    warnings.append([i,id_flow,id_cut])
                text.Reset()
            report.EndTable()
            text.Reset()
            # Displaying warnings
            if warning_test:
                report.CreateTable([12],text)
                report.NewCell()
                text.SetColor(ColorType.RED)
                text.Add("Warnings related to negative event-weights:")
                report.WriteText(text)
                report.NewLine()
                for item in warnings:
                    for line in self.cutflow.detail[i].warnings[id_flow][id_cut]:
                        report.NewCell()
                        text.Reset()
                        text.SetColor(ColorType.RED)
                        text.Add(line)
                        report.WriteText(text)
                        report.NewLine()
                report.EndTable()


    # Writing Statistics Table
    def WriteStatisticsTable(self,index,report):
        text=TextReport()
#        text.Add("Statistics table")
        report.CreateTable([2.6,2.5,2.0,2.1,2.1,2.1,2.1],text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        Dataset")
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add('        Integral')
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        Entries per event")
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        Mean")# (+/- err)")
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        RMS")# (+/- err)")
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        % underflow")
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        % overflow")
        report.WriteText(text)
        report.NewLine()

        # Looping over dataset
        warning_test=False
        for iset in range(0,len(self.plotflow.detail)):
            # Is there warning ?
            if len(self.plotflow.detail[iset][index].warnings)!=0:
                warning_test=True

            # Getting the number of entries
            integral = self.plotflow.detail[iset][index].summary.integral

            # Getting underflow and overflow
            uflow = self.plotflow.detail[iset][index].summary.underflow
            oflow = self.plotflow.detail[iset][index].summary.overflow

            # Computing underflow and overflow ratio / integral
            uflow_percent=0
            oflow_percent=0
            if integral!=0:
                uflow_percent = uflow*100/integral
                oflow_percent = oflow*100/integral
            # mean value
            mean = self.plotflow.detail[iset][index].summary.GetMean()

            # root mean square + error 
            rms = self.plotflow.detail[iset][index].summary.GetRMS()

            # writing the table
            report.NewCell()
            text.Reset()
            text.Add('        '+self.main.datasets[iset].name)
            report.WriteText(text)
            report.NewCell()

            # Nentries
            text.Reset()
            text.Add('        '+Layout.DisplayXsecCut(integral*self.plotflow.detail[iset][index].scale,0))
            report.WriteText(text)
            report.NewCell()

            # Getting the number of events and number of entries
            nentries = self.plotflow.detail[iset][index].summary.nentries
            nevents  = self.plotflow.detail[iset][index].summary.nevents

            # Nentries / Nevents
            text.Reset()

            if nevents!=0.:
                text.Add('        ' + \
                   str(Layout.Round_to_Ndigits(float(nentries)/float(nevents),3)))
            else:
                text.Add("        0.")
            report.WriteText(text)
            report.NewCell()

            # Mean value
            text.Reset()
            text.Add('        '+ str(Layout.Round_to_Ndigits(mean,6)))
#                  +"(+/- "+str(Layout.Round_to_Ndigits(mean_error,3))+")")
            report.WriteText(text)
            report.NewCell()
            text.Reset()
            text.Add('        '+str(Layout.Round_to_Ndigits(rms,4)))
#               +"(+/- "+str(Layout.Round_to_Ndigits(rms_error,3))+")")
            report.WriteText(text)
            if uflow_percent+oflow_percent<=5:
                report.NewCell(ColorType.GREEN)
            if uflow_percent+oflow_percent>5 and uflow_percent+oflow_percent<15:
                report.NewCell(ColorType.ORANGE)
            if uflow_percent+oflow_percent>15:
                report.NewCell(ColorType.RED)
            text.Reset()
            text.Add('        '+str(Layout.Round_to_Ndigits(uflow_percent,4)))
            report.WriteText(text)
            if uflow_percent+oflow_percent<=5:
                report.NewCell(ColorType.GREEN)
            if uflow_percent+oflow_percent>5 and uflow_percent+oflow_percent<15:
                report.NewCell(ColorType.ORANGE)
            if uflow_percent+oflow_percent>15:
                report.NewCell(ColorType.RED)
            text.Reset()
            text.Add('        '+str(Layout.Round_to_Ndigits(oflow_percent,4)))
            report.WriteText(text)
            if iset==(len(self.plotflow.detail)-1):
                report.EndLine()
            else: 
                report.NewLine()
        text.Reset()
        report.EndTable()

        text.Reset()

        # Displaying warnings
        if warning_test:
            report.CreateTable([12],text)
            report.NewCell()
            text.SetColor(ColorType.RED)
            text.Add("Warnings related to negative event-weights:")
            report.WriteText(text)
            report.NewLine()
            for iset in range(0,len(self.plotflow.detail)):
                for line in self.plotflow.detail[iset][index].warnings:
                    report.NewCell()
                    text.Reset()
                    text.SetColor(ColorType.RED)
                    text.Add(line)
                    report.WriteText(text)
                    report.NewLine()
            report.EndTable()

    # Writing Statistics Table
    def WriteStatisticsTablePID(self,index,report):
        text=TextReport()
        text.Add("Statistics table")
        report.CreateTable([2.6,4.1,2.3],text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        Dataset")
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add('        Integral')
        report.WriteText(text)
        report.NewCell(ColorType.YELLOW)
        text.Reset()
        text.Add("        Entries / events")
        report.WriteText(text)
        report.NewLine()

        # Looping over dataset
        warning_test=False
        for iset in range(0,len(self.plotflow.detail)):
            # Is there warning ?
            if len(self.plotflow.detail[iset][index].warnings)!=0:
                warning_test=True

            # Getting the number of entries
            integral = self.plotflow.detail[iset][index].summary.integral

            # writing the table
            report.NewCell()
            text.Reset()
            text.Add('        '+self.main.datasets[iset].name)
            report.WriteText(text)
            report.NewCell()

            # Nentries
            text.Reset()
            text.Add('        '+Layout.DisplayXsecCut(integral*self.plotflow.detail[iset][index].scale,0))
            report.WriteText(text)
            report.NewCell()

            # Getting the number of events and number of entries
            nentries = self.plotflow.detail[iset][index].summary.nentries
            nevents  = self.plotflow.detail[iset][index].summary.nevents

            # Nentries / Nevents
            text.Reset()

            if nevents!=0.:
                text.Add('        ' + \
                   str(Layout.Round_to_Ndigits(float(nentries)/float(nevents),3)))
            else:
                text.Add("        0.")
            report.WriteText(text)
            if iset==(len(self.plotflow.detail)-1):
                report.EndLine()
            else:
                report.NewLine()
        text.Reset()
        report.EndTable()
        text.Reset()

        # Displaying warnings
        if warning_test:
            report.CreateTable([12],text)
            report.NewCell()
            text.SetColor(ColorType.RED)
            text.Add("Warnings related to negative event-weights:")
            report.WriteText(text)
            report.NewLine()
            for iset in range(0,len(self.plotflow.detail)):
                for line in self.plotflow.detail[iset][index].warnings:
                    report.NewCell()
                    text.Reset()
                    text.SetColor(ColorType.RED)
                    text.Add(line)
                    report.WriteText(text)
                    report.NewLine()
            report.EndTable()


    def CreateFolders(self,histo_folder,output_paths,modes):

        # Creating histo folder
        if not FolderWriter.CreateDirectory(histo_folder,True):
            return False

        for ind in range(0,len(output_paths)):
                         
            # Creating production directory
            if not FolderWriter.CreateDirectory(output_paths[ind],True):
                return False

            # Copying MA5 logo
            if not self.CopyLogo(modes[ind],output_paths[ind]):
                return False
            
        return True


    def GenerateReport(self,history,output_path,mode):
        # Find a name for PDF file
        ma5_id = output_path.split('/')[-1]
        if self.main.session_info.has_pdflatex:
           self.pdffile=self.main.lastjob_name+'/Output/PDF/'+ma5_id+'/main.pdf'
        elif self.main.session_info.has_latex and self.main.session_info.has_dvipdf:
           self.pdffile=self.main.lastjob_name+'/Output/DVI/'+ma5_id+'/main.pdf'
        else:
           self.pdffile=''

        # Defining report writing
        if mode == ReportFormatType.HTML:
            mypdf=''
            if self.pdffile!='':
                mypdf=os.path.relpath(self.pdffile,output_path)
            report = HTMLReportWriter(output_path+"/index.html",mypdf)
        elif mode == ReportFormatType.LATEX:
            report = LATEXReportWriter(output_path+"/main.tex",\
              self.main.archi_info.ma5dir+"/madanalysis/input",False)
        else :
            report = LATEXReportWriter(output_path+"/main.tex",\
              self.main.archi_info.ma5dir+"/madanalysis/input",True)

        # Opening
        if not report.Open():
            return False

        # Create text
        text=TextReport()

        # Header
        report.WriteHeader()
        report.WriteTitle('MadAnalysis 5 report')

        # History of commands
        report.WriteSubTitle('Setup')
        report.WriteSubSubTitle('Command history')
        text.Reset()
        text.SetFont(FontType.TT)
        for item in history.history:
            text.Add('ma5>'+ item+'\n\n')
        report.WriteText(text)

        # Configuration
        report.WriteSubSubTitle('Configuration')

        # Integrated luminosity 
        report.OpenBullet()
        text.Reset()
        text.Add('MadAnalysis version ' + self.main.archi_info.ma5_version + \
                 ' (' + self.main.archi_info.ma5_date + ').\n')
        report.WriteText(text)

        # Integrated luminosity 
        text.Reset()

        # Normalization
        if self.main.normalize == NormalizeType.LUMI or \
           self.main.normalize == NormalizeType.LUMI_WEIGHT:
            text.Add('Histograms given for an integrated luminosity of ')
            text.SetColor(ColorType.BLUE)
            text.Add(str(self.main.lumi))
            text.Add(' fb')
            text.SetScript(ScriptType.SUP)
            text.Add('-1')
            text.SetScript(ScriptType.none)
            text.Add('.\n')
        elif self.main.normalize == NormalizeType.NONE:
            text.Add('Histograms are not scaled.\n')
        report.WriteText(text)
        report.CloseBullet()

        # Datasets
        report.WriteSubTitle('Datasets')
        for ind in range(0,len(self.main.datasets)):
            report.WriteSubSubTitle(self.main.datasets[ind].name)
            self.WriteDatasetTable(report,\
                                   self.main.datasets[ind])

        # Merging plots
        if self.main.merging.enable:

            # Title : merging plots
            report.WriteSubTitle('Merging plots')

            # Getting all plot names
            allnames = self.merging.GetPlotNames(mode,\
                                                 output_path)

            # Loop over datasets
            for i in range(0,len(allnames)):

                # Subtitle : dataset names
                report.WriteSubSubTitle(self.main.datasets[i].name)

                # Loop over DJR plots
                for j in range(0,len(allnames[i])):
                    text.Reset()
                    title = "DJR"+str(j+1)+" : "+str(j)
                    if j>1:
                        title +=" jets -> "
                    else:
                        title +=" jet -> "
                    title += str(j+1)
                    if j>0:
                        title += " jets"
                    else:
                        title += " jet"
                    text.Add(title)
                    if self.main.graphic_render!=GraphicRenderType.NONE:
                        report.WriteFigure(text,allnames[i][j])

        # Plots display
        if len(self.main.selection)!=0:
            report.WriteSubTitle('Histos and cuts')

        # Plots
        ihisto=0
        icut=0
        iobject=0
        cutinfo = []
        for ind in range(0,len(self.main.selection)):
            if self.main.selection[ind].__class__.__name__=="Histogram":
                report.WriteSubSubTitle("Histogram "+str(ihisto+1))
                text.Reset()
                text.SetFont(FontType.BF)
                text.Add(self.main.selection[ind].GetStringDisplay().lstrip())
                report.WriteText(text)
                text.Reset()
                text.SetFont(FontType.BF)
                report.NewBlankLine()
                if self.main.regions.GetNames()!=[]:
                    text.Add('* Regions: ')
                    text.SetFont(FontType.none)
                    for reg in self.main.selection[ind].regions:
                        text.Add(reg)
                        if reg!=self.main.selection[ind].regions[-1]:
                            text.Add(', ')
                    report.WriteText(text)
                    report.NewBlankLine()
                text.Reset()
                text.Add('\n\n')
                report.WriteText(text)
                text.Reset()
                text.Add('\n\n')
                if self.main.selection[ind].observable.name not in ['NPID','NAPID']:
                    self.WriteStatisticsTable(ihisto,report)
                else:
                    self.WriteStatisticsTablePID(ihisto,report)
                if self.main.graphic_render!=GraphicRenderType.NONE:
                    report.WriteFigure(text,output_path +'/selection_'+str(ihisto))
                text.Add('\n\n')
                report.WriteText(text)
                text.Reset()
                ihisto+=1
            elif self.main.selection[ind].__class__.__name__=="Cut":
                cutstring = self.main.selection[ind].GetStringDisplay().lstrip()
                if ', regions' in cutstring:
                    cutstring=cutstring[:cutstring.find(', regions')]
                cutregions =[]
                for reg in self.main.selection[ind].regions:
                    cutregions.append(reg)
                if cutregions == []:
                    cutregions = ['myregion']
                cutinfo.append([cutstring, cutregions, self.main.selection[ind].cut_type])
                if len(self.main.selection[ind].part)==0:
                    report.WriteSubSubTitle("Cut "+str(icut+1))
                    text.Reset()
                    text.SetFont(FontType.BF)
                    text.Add(cutstring)
                    report.WriteText(text)
                    text.Reset()
                    report.NewBlankLine()
                    text.SetFont(FontType.BF)
                    if self.main.regions.GetNames()!=[]:
                        text.Add('* Regions: ')
                        text.SetFont(FontType.none)
                        for reg in self.main.selection[ind].regions:
                            text.Add(reg)
                            if reg!=self.main.selection[ind].regions[-1]:
                                text.Add(', ')
                        report.WriteText(text)
                        report.NewBlankLine()
                    text.Reset()
                    text.Add('\n\n')
                    report.WriteText(text)
                    text.Reset()
                    self.WriteEfficiencyTable(ind,icut,report)
                    text.Add('\n\n')
                    report.WriteText(text)
                    text.Reset()
                    icut+=1
                else:
                    report.WriteSubSubTitle("Object definition "+str(iobject+1))
                    text.Reset()
                    text.SetFont(FontType.BF)
                    text.Add(cutstring)
                    report.WriteText(text)
                    text.Reset()
                    report.NewBlankLine()
                    text.SetFont(FontType.BF)
                    if self.main.regions.GetNames()!=[]:
                        text.Add('* Regions: ')
                        text.SetFont(FontType.none)
                        for reg in self.main.selection[ind].regions:
                            text.Add(reg)
                            if reg!=self.main.selection[ind].regions[-1]:
                                text.Add(', ')
                        report.WriteText(text)
                        report.NewBlankLine()
                    text.Reset()
                    text.Add('\n\n')
                    report.WriteText(text)
                    text.Reset()
                    iobject+=1

        # Final table
        if self.main.selection.Ncuts!=0:
            report.WriteSubTitle('Summary')
            report.WriteSubSubTitle('Cut-flow charts')
            self.WriteFinalTable(report,cutinfo)

        # Foot
        report.WriteFoot()

        # Closing
        report.Close()

        return True


    @staticmethod
    def CheckLatexLog(file):
        if not os.path.isfile(file):
            return False
        for line in file:
            if line.startswith('!'):
                return False
        return True

    def CompileReport(self,mode,output_path):
        
        # ---- LATEX MODE ----
        if mode==ReportFormatType.LATEX:

            # Launching latex and producing DVI file
            os.system('cd '+output_path+'; latex -interaction=nonstopmode main.tex > latex.log 2>&1; latex -interaction=nonstopmode main.tex >> latex.log 2>&1')

            name=os.path.normpath(output_path+'/main.dvi')
            if not os.path.isfile(name):
                self.logger.error('DVI file cannot be produced')
                self.logger.error('Please have a look to the log file '+output_path+'/latex.log')
                return False
            
            # Checking latex log : are there errors
            if not Layout.CheckLatexLog(output_path+'/latex.log'):
                self.logger.error('some errors occured during LATEX compilation')
                self.logger.error('for more details, have a look to the log file : '+output_path+'/latex.log')
                return False

            # Converting DVI file to PDF file
#            if self.main.session_info.has_dvipdf:
#                self.logger.info("     -> Converting the DVI report to a PDF report.")
#                os.system('cd '+output_path+'; dvipdf main.dvi > dvipdf.log 2>&1')
#                name=os.path.normpath(output_path+'/main.pdf')
#
#                # Checking PDF file presence
#                if not os.path.isfile(name):
#                    self.logger.error('PDF file cannot be produced')
#                    self.logger.error('Please have a look to the log file '+output_path+'/dvipdf.log')
#                    return False

        # ---- PDFLATEX MODE ----
        elif mode==ReportFormatType.PDFLATEX:

            # Launching latex and producing PDF file
            os.system('cd '+output_path+'; pdflatex -interaction=nonstopmode main.tex > latex.log 2>&1; pdflatex -interaction=nonstopmode main.tex >> latex.log 2>&1');

            # Checking latex log : are there errors
            if not Layout.CheckLatexLog(output_path+'/latex.log'):
                self.logger.error('some errors occured during LATEX compilation')
                self.logger.error('for more details, have a look to the log file : '+output_path+'/latex.log')
                return False

            # Checking PDF file presence
            name=os.path.normpath(output_path+'/main.pdf')
            if not os.path.isfile(name):
                self.logger.error('PDF file cannot be produced')
                self.logger.error('Please have a look to the log file '+output_path+'/latex2.log')
                return False
