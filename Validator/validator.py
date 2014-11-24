##@package validator
# Validation code for the PxlAnalyzer in the TAPAS framework
#
# This package runs the analysis and measures its performance.
# It then compares the performance and analysis output with
# A reference output. If there are differences the user has to
# decide if they are expected or if they need more work. If
# the validation is successfull new reference distributions
# are created and the new analysis is pushed to the central
# repository.
#
# written by Soeren Erdweg 2014

#!/bin/env python

import optparse, time, os, subprocess, sys
import resource
from datetime import datetime
from array import array
import numpy as np
import logging
import multiprocessing
sys.path.append("lib/")
from configobj import ConfigObj
import StringIO
from math import sqrt, fabs
import matplotlib.pyplot as plt
from matplotlib import transforms
from matplotlib import rc
rc('text', usetex=True)

import ROOT as ro
from ROOT import TCanvas, TGraph, TF1, TLegend, kBlue, gStyle, gPad, TPad, TFile, TStyle, TColor, TH1F

log = logging.getLogger( 'Validator' )

tdrStyle = TStyle("tdrStyle","Style for P-TDR");

ro.gROOT.ProcessLine( "gErrorIgnoreLevel = 3001;")
compare_results = {}

## Function to get the size of the terminal
#
# Reads the width and height of the current terminal and returns
# this two values.
# @param[out] int(cr[1]) Width of the terminal
# @param[out] int(cr[0]) Height of the terminal
class bcolors:
    HEADER = '\033[35m'
    OKBLUE = '\033[34m'
    OKGREEN = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    ENDC = '\033[0m'

    ## Function to unset all colors
    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.CYAN = ''
        self.WHITE = ''
        self.ENDC = ''

def setTDRStyle(logy):
    global tdrStyle

    # For the canvas:
    tdrStyle.SetCanvasBorderMode(0);
    tdrStyle.SetCanvasColor(ro.kBlack);
    tdrStyle.SetCanvasDefH(1000); #Height of canvas
    tdrStyle.SetCanvasDefW(800); #Width of canvas
    tdrStyle.SetCanvasDefX(0);   #POsition on screen
    tdrStyle.SetCanvasDefY(0);
    # For the Pad:
    tdrStyle.SetPadBorderMode(0);
    # tdrStyle.SetPadBorderSize(Width_t size = 1);
    tdrStyle.SetPadColor(ro.kBlack);
    tdrStyle.SetPadGridX(True);
    tdrStyle.SetPadGridY(True);
    tdrStyle.SetGridColor(ro.kWhite);
    tdrStyle.SetGridStyle(3);
    tdrStyle.SetGridWidth(1);

    # For the frame:
    tdrStyle.SetFrameBorderMode(0);
    tdrStyle.SetFrameBorderSize(1);
    tdrStyle.SetFrameFillColor(0);
    tdrStyle.SetFrameFillStyle(0);
    tdrStyle.SetFrameLineColor(ro.kWhite);
    tdrStyle.SetFrameLineStyle(1);
    tdrStyle.SetFrameLineWidth(1);

    # For the histo:
    # tdrStyle.SetHistFillColor(1);
    # tdrStyle.SetHistFillStyle(0);
    tdrStyle.SetHistLineColor(1);
    tdrStyle.SetHistLineStyle(0);
    tdrStyle.SetHistLineWidth(2);
    # tdrStyle.SetLegoInnerR(Float_t rad = 0.5);
    # tdrStyle.SetNumberContours(Int_t number = 20);

    tdrStyle.SetEndErrorSize(2);
    #  tdrStyle.SetErrorMarker(20);
    tdrStyle.SetErrorX(0.);

    #tdrStyle.SetMarkerStyle(20);

    #For the fit/function:
    tdrStyle.SetOptFit(0);
    tdrStyle.SetFitFormat("5.4g");
    tdrStyle.SetFuncColor(2);
    tdrStyle.SetFuncStyle(1);
    tdrStyle.SetFuncWidth(1);

    #For the date:
    tdrStyle.SetOptDate(0);
    # tdrStyle.SetDateX(Float_t x = 0.01);
    # tdrStyle.SetDateY(Float_t y = 0.01);

    # For the statistics box:
    tdrStyle.SetOptFile(0);
    tdrStyle.SetOptStat("emr"); # To display the mean and RMS:   SetOptStat("mr");
    tdrStyle.SetStatColor(ro.kWhite);
    tdrStyle.SetStatFont(42);
    tdrStyle.SetStatFontSize(0.025);
    tdrStyle.SetStatTextColor(1);
    tdrStyle.SetStatFormat("6.4g");
    tdrStyle.SetStatBorderSize(1);
    tdrStyle.SetStatH(0.1);
    tdrStyle.SetStatW(0.15);
    # tdrStyle.SetStatStyle(Style_t style = 1001);
    # tdrStyle.SetStatX(Float_t x = 0);
    # tdrStyle.SetStatY(Float_t y = 0);

    # Margins:
    tdrStyle.SetPadTopMargin(0.05);
    tdrStyle.SetPadBottomMargin(0.13);
    tdrStyle.SetPadLeftMargin(0.13);
    tdrStyle.SetPadRightMargin(0.05);

    # For the Global title:
    tdrStyle.SetOptTitle(0);
    tdrStyle.SetTitleFont(42);
    tdrStyle.SetTitleColor(1);
    tdrStyle.SetTitleTextColor(1);
    tdrStyle.SetTitleFillColor(10);
    tdrStyle.SetTitleFontSize(0.05);
    # tdrStyle.SetTitleH(0); # Set the height of the title box
    # tdrStyle.SetTitleW(0); # Set the width of the title box
    # tdrStyle.SetTitleX(0); # Set the position of the title box
    # tdrStyle.SetTitleY(0.985); # Set the position of the title box
    # tdrStyle.SetTitleStyle(Style_t style = 1001);
    # tdrStyle.SetTitleBorderSize(2);

    # For the axis titles:
    tdrStyle.SetTitleColor(ro.kWhite, "XYZ");
    tdrStyle.SetTitleFont(42, "XYZ");
    tdrStyle.SetTitleSize(0.06, "XYZ");
    # tdrStyle.SetTitleXSize(Float_t size = 0.02); # Another way to set the size?
    # tdrStyle.SetTitleYSize(Float_t size = 0.02);
    tdrStyle.SetTitleXOffset(0.9);
    tdrStyle.SetTitleYOffset(1.05);
    # tdrStyle.SetTitleOffset(1.1, "Y"); # Another way to set the Offset

    # For the axis labels:
    tdrStyle.SetLabelColor(ro.kWhite, "XYZ");
    tdrStyle.SetLabelFont(42, "XYZ");
    tdrStyle.SetLabelOffset(0.007, "XYZ");
    tdrStyle.SetLabelSize(0.05, "XYZ");

    # For the axis:
    tdrStyle.SetAxisColor(ro.kWhite, "XYZ");
    tdrStyle.SetStripDecimals(ro.kTRUE);
    tdrStyle.SetTickLength(0.03, "XYZ");
    tdrStyle.SetNdivisions(508, "XYZ");
    tdrStyle.SetPadTickX(1);  # To get tick marks on the opposite side of the frame
    tdrStyle.SetPadTickY(1);

    # Change for log plots:
    tdrStyle.SetOptLogx(0);
    tdrStyle.SetOptLogy(logy);
    tdrStyle.SetOptLogz(0);

    # Postscript options:
    tdrStyle.SetPaperSize(20.,20.);

    tdrStyle.SetPalette(1);
    
    NRGBs = 5;
    NCont = 255;

    stops = [ 0.00, 0.34, 0.61, 0.84, 1.00 ]
    red   = [ 0.00, 0.00, 0.87, 1.00, 0.51 ]
    green = [ 0.00, 0.81, 1.00, 0.20, 0.00 ]
    blue  = [ 0.51, 1.00, 0.12, 0.00, 0.00 ]
    TColor.CreateGradientColorTable(NRGBs, array("d",stops), array("d", red), array("d",green ), array("d", blue), NCont);
    #TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont);
    #TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont);
    tdrStyle.SetNumberContours(NCont);
    #gROOT.ForceStyle();
    tdrStyle.cd();

def opt_parser():
    date_time = datetime.now()
    usage = '%prog [options] CONFIG_FILE'
    parser = optparse.OptionParser( usage = usage )
    parser.add_option( '-u', '--user', default = os.getenv( 'LOGNAME' ),
                            help = 'which user on dcache [default = %s]'%(os.getenv( 'LOGNAME' )))
    parser.add_option( '-o', '--Output', default = "./output", metavar = 'DIRECTORY',
                            help = 'Define the output directory. [default = %default]')
    parser.add_option( '--debug', metavar = 'LEVEL', default = 'INFO',
                       help= 'Set the debug level. Allowed values: ERROR, WARNING, INFO, DEBUG. [default = %default]' )

    parser.add_option( '--executable', metavar = 'EXECUTABLE' , default = 'music',
                            help = 'Name of the executable. [default = %default]')
    parser.add_option( '--exeoption', metavar = 'EXEOPTION' , default = '--SpecialAna',
                            help = 'Options that should be passed to the executable. [default = %default]' )
    parser.add_option( '--execonfig', metavar = 'EXECONFIG' , default = '$MUSIC_BASE/ConfigFiles/MC.cfg',
                            help = 'Configuration file that should be passed to the executable. [default = %default]')
    parser.add_option( '--cfgfile', metavar = 'CFGFILE' , default = './config.cfg',
                            help = 'Name of the configuration file for the used files. [default = %default]' )
    parser.add_option( '--compdir', metavar = 'COMPDIR' , default = './old',
                            help = 'Directory of the files that should be used for the comparison. [default = %default]')
    parser.add_option( '--memtolerance', metavar = 'MEMTOLERANCE' , default = 10.,
                            help = 'Accepted tolerance of memory usage in percent. [default = %default]' )
    parser.add_option( '--timetolerance', metavar = 'TIMETOLERANCE' , default = 100.,
                            help = 'Accepted tolerance of run time in percent. [default = %default]' )
    parser.add_option( '--allplots', metavar = 'ALLPLOTS' , default = False,
                            help = 'Bool if all plots should be made or only plots with Chi2 != 0. [default = %default]' )

    ( options, args ) = parser.parse_args()
    if len( args ) != 0:
        parser.error( 'Exactly zero CONFIG_FILE required!' )

    format = '%(levelname)s from %(name)s at %(asctime)s: %(message)s'
    date = '%F %H:%M:%S'
    logging.basicConfig( level = logging._levelNames[ options.debug ], format = format, datefmt = date )

    try: 
        cfg_file= ConfigObj(options.cfgfile)
    except IOError as e:
        log.error("There was a error reading the File "+ options.cfgfile)
        log.error(e)
        exit()


    return args,options,cfg_file

def make_new_reference():
    control_output("making new reference plots",True,True)

def check_authorization():
    control_output("Now checking the user authorization",True,True)
    return False

def make_commits():
    control_output("Now making the final commits",True,True)

def final_user_decision():
    raw_input("waiting for the final user decision")
    return False

def control_output(histogram,value,group):
    if group == True:
        log.info(" ")
        log.info(25*"-")
        log.info("\t"+histogram)
        log.info(25*"-")
        log.info(" ")
    else:
        text = "\t"
        text += histogram
        text += ":  "
        if value == True:
            text += bcolors.OKGREEN
            text += "Okay"
            text += bcolors.ENDC
        else:
            text += bcolors.FAIL
            text += "Problem"
            text += bcolors.ENDC
        log.info(text)

def draw_mem_histos(old_rss_histos,old_rss_time,p_color,ax):
    old_rss_line = ro.TLine(np.mean(old_rss_time),0,np.mean(old_rss_time),1)

    dummy_x_vals = []
    dummy_y_vals = []
    for item in old_rss_histos:
        temp_x_vals = []
        temp_y_vals = []
        for i in range(0,item.GetN()-1):
            dummy_value = ro.Double(0)
            dummy_value2 = ro.Double(0)
            item.GetPoint(i,dummy_value,dummy_value2)
            dummy_x_vals.append(dummy_value)
            dummy_y_vals.append(dummy_value2)
            temp_x_vals.append(dummy_value)
            temp_y_vals.append(dummy_value2)
        plt.plot(temp_x_vals, temp_y_vals,color=p_color,marker="o",linestyle="-",linewidth=1)
    plt.xlim( 0, np.max(dummy_x_vals)*1.05 )
    plt.ylim( np.min(dummy_y_vals)*0.95, np.max(dummy_y_vals)*1.05 )
    mean_graph = ro.TGraph(len(dummy_x_vals),array("d",dummy_x_vals),array("d",dummy_y_vals))
    res_fit = ro.TF1(old_rss_histos[0].GetName()+"_f1","pol1",np.min(dummy_x_vals),np.max(dummy_x_vals))
    mean_graph.Fit(res_fit,"Q+","",np.min(dummy_x_vals)+4,np.max(dummy_x_vals)-4)
    l = plt.axvline(x=np.mean(old_rss_time),color='tomato')
    text = ax.text(np.mean(old_rss_time)+0.5, np.min(dummy_y_vals), 'mean run time: %.1f s'%(np.mean(old_rss_time)), color='tomato',
                rotation=90, va='bottom', ha='left')
    X = np.linspace(np.min(dummy_x_vals),np.max(dummy_x_vals), 256, endpoint=True)
    Y = res_fit.GetParameter(0) + X * res_fit.GetParameter(1)
    plt.plot(X,Y,color='limegreen',linewidth=2)
    text = ax.text((np.max(dummy_x_vals)*1.05)/2., np.min(dummy_y_vals), 'memory usage: %.1f MB'%(res_fit.Eval(np.mean(old_rss_time))), color='limegreen',
                va='bottom', ha='center')
    return ax,res_fit.Eval(np.mean(old_rss_time)),np.mean(old_rss_time)

def make_axis(ax,x_title,y_title,title):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(0.5)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')

    ax.title.set_color('black')
    ax.yaxis.label.set_color('black')
    ax.xaxis.label.set_color('black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')

    ax.tick_params(axis='both', direction='in')
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title)
    ax.set_title(title)

def comparison_performance(options):
    log.debug("comparing the programs performance")

    log.debug("reading the comparison histos")
    comp_log_file = TFile("comparison_dir/old/log.root","READ")

    old_rss_histos = []
    old_rss_time = []
    old_vir_histos = []
    old_vir_time = []
    for key in comp_log_file.GetListOfKeys():
        dummy_name = key.GetName()
        if "_rss" in dummy_name:
            dummy_hist = comp_log_file.Get(dummy_name)
            dummy_hist.SetName(dummy_name)
            dummy_value = ro.Double(0)
            dummy_value2 = ro.Double(0)
            dummy_hist.GetPoint(dummy_hist.GetN()-1,dummy_value,dummy_value2)
            old_rss_time.append(dummy_value)
            old_rss_histos.append(dummy_hist)
        if "_vir" in dummy_name:
            dummy_hist = comp_log_file.Get(dummy_name)
            dummy_hist.SetName(dummy_name)
            dummy_value = ro.Double(0)
            dummy_value2 = ro.Double(0)
            dummy_hist.GetPoint(dummy_hist.GetN()-1,dummy_value,dummy_value2)
            old_vir_time.append(dummy_value)
            old_vir_histos.append(dummy_hist)
    comp_log_file.Close()

    log.debug("reading the new histos")
    new__log_file = TFile("comparison_dir/new/log.root","READ")

    new_rss_histos = []
    new_rss_time = []
    new_vir_histos = []
    new_vir_time = []
    for key in new__log_file.GetListOfKeys():
        dummy_name = key.GetName()
        if "_rss" in dummy_name:
            dummy_hist = new__log_file.Get(dummy_name)
            dummy_hist.SetName(dummy_name)
            dummy_value = ro.Double(0)
            dummy_value2 = ro.Double(0)
            dummy_hist.GetPoint(dummy_hist.GetN()-1,dummy_value,dummy_value2)
            new_rss_time.append(dummy_value)
            new_rss_histos.append(dummy_hist)
        if "_vir" in dummy_name:
            dummy_hist = new__log_file.Get(dummy_name)
            dummy_hist.SetName(dummy_name)
            dummy_value = ro.Double(0)
            dummy_value2 = ro.Double(0)
            dummy_hist.GetPoint(dummy_hist.GetN()-1,dummy_value,dummy_value2)
            new_vir_time.append(dummy_value)
            new_vir_histos.append(dummy_hist)
    new__log_file.Close()

    fig = plt.figure(figsize=(10, 10), dpi=80, facecolor='white')
 
    ax = fig.add_subplot(2,2,1,axisbg='white')
    make_axis(ax,'run time (s)','memory (MB)','old')
    ax,old_rss_usage,old_rss_time = draw_mem_histos(old_rss_histos,old_rss_time,"y",ax)

    ax = fig.add_subplot(2,2,2,axisbg='white')
    make_axis(ax,'run time (s)','virtual memory (MB)','old')
    ax,old_vir_usage,old_vir_time = draw_mem_histos(old_vir_histos,old_vir_time,"royalblue",ax)

    ax = fig.add_subplot(2,2,3,axisbg='white')
    make_axis(ax,'run time (s)','memory (MB)','new')
    ax,new_rss_usage,new_rss_time = draw_mem_histos(new_rss_histos,new_rss_time,"orange",ax)

    ax = fig.add_subplot(2,2,4,axisbg='white')
    make_axis(ax,'run time (s)','virtual memory (MB)','new')
    ax,new_vir_usage,new_vir_time = draw_mem_histos(new_vir_histos,new_vir_time,"cornflowerblue",ax)

    diff_rss = (old_rss_usage - new_rss_usage)/ old_rss_usage * 100
    diff_time = (old_rss_time - new_rss_time)/ old_rss_time * 100
    diff_vir = (old_vir_usage - new_vir_usage)/ old_vir_usage * 100

    if diff_rss > 0.:
        text = fig.text(0.25 , 0.01, 'memory difference: %+.1f %% \n time difference: %+.1f %%'%(diff_rss,diff_time), color='chartreuse',
                va='bottom', ha='center', fontsize=20)
        text.set_zorder(20)
    else:
        text = fig.text(0.25, 0.01, 'memory difference: %+.1f %% \n time difference: %+.1f %%'%(diff_rss,diff_time), color='red',
                va='bottom', ha='center', fontsize=20)
        text.set_zorder(20)

    if diff_vir > 0.:
        text = fig.text(0.75, 0.01, 'memory difference: %+.1f %% \n time difference: %+.1f %%'%(diff_vir,diff_time), color='chartreuse',
                va='bottom', ha='center', fontsize=20)
        text.set_zorder(20)
    else:
        text = fig.text(0.75, 0.01, 'memory difference: %+.1f %% \n time difference: %+.1f %%'%(diff_vir,diff_time), color='red',
                va='bottom', ha='center', fontsize=20)
        text.set_zorder(20)

    plt.show()
    plt.savefig("comparison_dir/mem_comparison.pdf",facecolor='white',edgecolor='white')

    if diff_time < -1 * options.timetolerance:
        compare_results.update({"performance":[False,diff_time,diff_rss]})
        return False
    elif diff_rss < -1 * options.memtolerance:
        compare_results.update({"performance":[False,diff_time,diff_rss]})
        return False
    else:
        compare_results.update({"performance":[True,diff_time,diff_rss]})
        return True

def comparison_norm(item,hist,fname):
    log.debug("comparing the normalization of distributions")

    log.debug("Now reading: " +item+"/"+hist + " from: comparison_dir/old/%s.root"%(fname))
    comp_file = TFile("comparison_dir/old/%s.root"%(fname),"READ")
    ref_hist = TH1F()
    ref_hist = comp_file.Get(item+"/"+hist)
    ref_hist.SetDirectory(0)
    comp_file.Close()
    new_file = TFile("comparison_dir/new/%s.root"%(fname),"READ")
    new_hist = TH1F()
    new_hist = new_file.Get(item+"/"+hist)
    new_hist.SetDirectory(0)
    new_file.Close()

    if ref_hist.GetEntries() == 0 and new_hist.GetEntries() == 0:
        compare_results[fname + "_" + item + "_" + hist] = [True,0,0]
        return True

    chi2 = Chi2_calcer(ref_hist,new_hist)

    if chi2 == 0.0:
        compare_results[fname + "_" + item + "_" + hist] = [True,0,0]
        return True
    else:
        compare_results[fname + "_" + item + "_" + hist] = [False,chi2,0]
        return False

def comparison_events(item,hist,fname):
    log.debug("comparing the number of events in the distribution")

    log.debug("Now reading: " +item+"/"+hist + " from: comparison_dir/old/%s.root"%(fname))
    comp_file = TFile("comparison_dir/old/%s.root"%(fname),"READ")
    ref_hist = TH1F()
    ref_hist = comp_file.Get(item+"/"+hist)
    ref_hist.SetDirectory(0)
    comp_file.Close()
    new_file = TFile("comparison_dir/new/%s.root"%(fname),"READ")
    new_hist = TH1F()
    new_hist = new_file.Get(item+"/"+hist)
    new_hist.SetDirectory(0)
    new_file.Close()

    diff = ref_hist.GetEntries() - new_hist.GetEntries()

    compare_results[fname + "_" + item + "_" + hist] = [compare_results[fname + "_" + item + "_" + hist][0],compare_results[fname + "_" + item + "_" + hist][1],diff]

def do_comparison(options,cfg_file,sample_list):
    control_output("doing the comparison",True,True)

    c_performance = comparison_performance(options)
    control_output("performance",True,True)
    control_output("performance",c_performance,False)

    histos = {}
    for group in cfg_file["basic"]["hist_groups"]:
        dummy_histos = []
        for item in cfg_file["histos"]:
            if cfg_file["histos"][item]["folder"] == group:
                dummy_histos.append(item)
                log.debug("Now adding histogram: " + item)
        histos.update({group:dummy_histos})
    log.debug(histos)

    all_samples = True
    for i_sample in sample_list:
        all_hists = True
        fname = i_sample
        for item in histos:
            control_output(item,True,True)

            group = True
            for hist in histos[item]:
                log.debug("Now comparing: " + hist)
                compare_results.update({i_sample + "_" + item + "_" + hist:[False,0,0]})
                c_norm = comparison_norm(item,hist,fname)
                control_output(hist,True,False)
                group = group and c_norm

                if not c_norm:
                    comparison_events(item,hist,fname)

                    #c_shape = comparison_shape(item,hist,fname)

                    ##if c_norm and c_shape and c_events:
                        ##control_output(hist,True,False)
                    ##else:
                        ##control_output(hist+" norm",c_norm,False)
                        ##control_output(hist+" shape",c_shape,False)
                        ##control_output(hist+" events",c_events,False)
                    #group = group and c_norm and c_shape and c_events
                #else:
                    #control_output(hist,True,False)
                    #group = group and c_norm
            #log.info(" ")
            #control_output(item,group,False)
            all_hists = all_hists and group
        control_output("All histograms",True,True)
        control_output("All histograms",all_hists,False)
        all_samples = all_samples and all_hists
    control_output("All samples",True,True)
    control_output("All samples",all_samples,False)

def get_reference_output(options):
    control_output("getting the reference output",True,True)

    if not os.path.exists("comparison_dir/old"):
        os.mkdir("comparison_dir/old")

    p = subprocess.Popen("cp %s/*.root comparison_dir/old/"%(options.compdir),shell=True,stdout=subprocess.PIPE)
    output = p.communicate()[0]

def get_analysis_output(options):
    control_output("getting the analysis output",True,True)

    if not os.path.exists("comparison_dir"):
        os.mkdir("comparison_dir")
    if not os.path.exists("comparison_dir/new"):
        os.mkdir("comparison_dir/new")

    p = subprocess.Popen("cp %s/*.root comparison_dir/new/"%(options.Output),shell=True,stdout=subprocess.PIPE)
    output = p.communicate()[0]

def get_sample_list(cfg_file):
    sample_list = []
    for item in cfg_file["samples"]:
        if cfg_file["samples"][item]["label"] not in sample_list:
            sample_list.append(cfg_file["samples"][item]["label"])
    return sample_list

def run_analysis(options,cfg_file,sample_list):
    control_output("running the analysis",True,True)

    music_prog = options.executable
    music_opt  = options.exeoption
    music_cfg  = options.execonfig
    music_path = cfg_file["basic"]["path"]

    item_list = []
    for item in cfg_file["samples"]:
        item_list.append([music_prog,"-o %s"%(item[item.find("/")+1:-6]),music_opt,music_cfg,music_path+item])
    pool = multiprocessing.Pool()
    pool.map_async(run_analysis_task, item_list)
    while True:
        time.sleep(1)
        if not pool._cache: break
    pool.close()
    pool.join()

    if not os.path.exists(options.Output):
        os.mkdir(options.Output)

    p = subprocess.Popen("hadd -f9 %s/%s *_mem_log.root"%(options.Output,"log.root"),shell=True,stdout=subprocess.PIPE)
    output = p.communicate()[0]

    for item in sample_list:
        sample_files = []
        sample_folders = []
        for item2 in cfg_file["samples"]:
            if cfg_file["samples"][item2]["label"] == item:
                sample_files.append(item2[item2.find("/")+1:-6]+"/SpecialHistos.root")
                sample_folders.append(item2[item2.find("/")+1:-6])
        p3 = subprocess.Popen("hadd -f9 %s/%s.root "%(options.Output,item)+" ".join(sample_files),shell=True,stdout=subprocess.PIPE)
        output = p3.communicate()[0]
        for item2 in sample_folders:
            p2 = subprocess.Popen("rm -r %s"%item2,shell=True,stdout=subprocess.PIPE)
            output = p2.communicate()[0]

    p4 = subprocess.Popen("rm *.root",shell=True,stdout=subprocess.PIPE)
    output = p4.communicate()[0]

def run_analysis_task(item):
    usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    rssList = []
    virtual = []
    other = []
    cmd = [item[0], item[1], item[2], item[3], item[4]]
    log.debug(" ".join(cmd))
    #print(" ".join(cmd))
    p = subprocess.Popen(" ".join(cmd), shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    pid = p.pid
    while True:
        if p.poll() != None:
            break
        p2 = subprocess.Popen("top -b -n 1 -p %s | grep %s"%(pid,pid),shell=True,stdout=subprocess.PIPE)
        output = p2.communicate()[0]
        if output != '':
            if "m" in output.split()[5]:
                rssList.append(output.split()[5].split("m")[0]) 
            else:
                rssList.append(output.split()[5]) 
            if "m" in output.split()[4]:
                virtual.append(output.split()[4].split("m")[0]) 
            else:
                virtual.append(output.split()[4])
        time.sleep(1)

    output = p.communicate()[0]
    exitCode = p.returncode
    if exitCode != 0:
        log.error("exitCode: " + str(exitCode))
        log.error(output,p.communicate()[1])
    else:
        log.debug("exitCode: " + str(exitCode))
        log.debug(output)
    usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_time = usage_end.ru_utime - usage_start.ru_utime

    rssArray = np.array(rssList,"d")
    virtualArray = np.array(virtual,"d")
    xAxis = []
    for i in range(0,len(rssArray)):
        xAxis.append(i*(cpu_time/len(rssArray)))

    xAxisArray = np.array(xAxis,"d")
    graphRSS = TGraph(len(rssArray),xAxisArray,rssArray)
    graphVirtual = TGraph(len(virtualArray),xAxisArray,virtualArray)

    graphRSS.SetMarkerColor(kBlue)
    graphRSS.SetMarkerStyle(21)

    dummy_file = TFile(item[1][3:]+"_mem_log.root","RECREATE")

    graphRSS.Write(item[1][3:]+"_rss")
    graphVirtual.Write(item[1][3:]+"_vir")

    dummy_file.Close()

def create_tex_summary(content,sample_list,cfg_file,options):
    log.debug("Now creating the title page for the .tex document")
## Create the Title page
    content += r'''
This is the summary of the validation from \today
\pagebreak
\tableofcontents
\pagebreak
'''

    log.debug("Creating the summary table")
## Create the summary table
    content += r'''
\section{Summary table}
\subsection{Performance}
\begin{itemize}
'''
    if compare_results["performance"][0]:
        content += r'''
\item Performance: {\color{darkgreen}True}
\end{itemize}
'''
    else:
        content += r'''
\item Performance: {\color{red}False  } Run time difference (%): %.2f    Memory usage difference (%): %.2f"
\end{itemize}
'''%(compare_results["performance"][1],compare_results["performance"][2])
    for sample in sample_list:
        content += r'''
\subsection{%s}
'''%(sample)
        for folder in cfg_file["basic"]["hist_groups"]:
            content += r'''
\subsubsection{%s}
\begin{itemize}
'''%(folder)
            for i in compare_results:
                if sample in i and folder in i:
                    dummy_string = ""
                    if compare_results[i][0]:
                        if options.allplots:
                            dummy_string += "{\color{darkgreen}True} Fig.~\\ref{fig:%s!%s!%s}"%(sample,folder,i[i.find(folder)+len(folder)+1:].replace("_","!"))
                        else:
                            dummy_string += "{\color{darkgreen}True}"
                    else:
                        dummy_string += '''{\color{red}False  } Fig.~\\ref{fig:%s!%s!%s}\\\\
$\chi^{2}$: %.2f \hspace{1cm} $N!{events}^{reference} - N!{events}^{new}: $%.2f'''%(sample,folder,i[i.find(folder)+len(folder)+1:].replace("_","!"),compare_results[i][1],compare_results[i][2])
                    content += r'''
\item %s: %s
'''%(i[i.find(folder)+len(folder)+1:],dummy_string)
            content += r'''
\end{itemize}
'''
    log.debug("done")
## End of summary table
    content += r'''
\pagebreak
'''

## Include Plot with Chi2 distribution
    content += r'''
\section{Overview}
\includegraphics[width=15cm]{%s}
'''%("comparison!dir/chi2!distribution.pdf")

    log.debug("Creating the comparison plots for the .tex file")
## Include the performance Plots
    content += r'''
\section{Performance}
\includegraphics[width=15cm]{%s}
'''%("comparison!dir/mem!comparison.pdf")
    chi2_vals = []
## Create the different histograms
    for sample in sample_list:
        content += r'''
\section{%s}
'''%(sample)
        for folder in cfg_file["basic"]["hist_groups"]:
            log.debug("Now working on %s"%(folder))
            content += r'''
\subsubsection{%s}
'''%(folder)
            hist_list = []
            for i in compare_results:
                if sample in i and folder in i:
                    hist_list.append([sample,folder,i,options])
            #new_hist_list = []
            #counter = 0
            #for item in hist_list:
                #dummy = make_comparison_plot(item)
                #if not options.allplots:
                    #if dummy[0] != "NONE" and dummy[1] != 0.0:
                        #new_hist_list.append(dummy)
                #else:
                    #new_hist_list.append(dummy)
                #counter += 1
                #update_progress(float(counter)/len(hist_list))
            pool = multiprocessing.Pool()
            test = pool.map_async(make_comparison_plot, hist_list)
            while True:
                time.sleep(1)
                if not pool._cache: break
            pool.close()
            pool.join()
            try:
                new_hist_list = test.get(timeout=1)
            except:
                time.sleep(5)
                try:
                    new_hist_list = test.get(timeout=1)
                except:
                    log.error("Could not get the plotting output, try restarting the validator")
            hist_list = sorted(new_hist_list, key=lambda hist: hist[1], reverse=True)
            for i in hist_list:
                content += r'''
\begin{figure}[hbtp]
\centering
\includegraphics[width=15cm]{%s}
\caption{%s}
\label{fig:%s!%s!%s}
\end{figure}
'''%(i[0].replace("_","!"),i[0],sample,folder,i[0][i[0].find(folder)+len(folder)+1:-4].replace("_","!"))
                chi2_vals.append(i[1])
            log.debug("done")
    log.debug("done")

    make_chi2_distribution(chi2_vals)

    return content

def make_chi2_distribution(chi2_vals):
    log.debug("Now plotting: Chi2 distribution")
    fig = plt.figure(figsize=(8, 8), dpi=20, facecolor='white')
    ax = fig.add_subplot(111)
    make_axis(ax,"$\chi^{2} values$","Number of Distributions","")
    min_val = 0.1 * np.min(chi2_vals)
    if min_val == 0:
        min_val = 0.000001
    binning = np.logspace(np.log10(min_val), np.log10(np.max(chi2_vals)), num=100, base=10.)
    log.debug(binning,np.log10(min_val),np.log10(np.max(chi2_vals)))
    n, bins, patches = plt.hist(chi2_vals, bins=binning, facecolor='green', alpha=0.75)
    plt.grid(True)
    ax.set_xscale("symlog")
    plt.show()
    plt.savefig("comparison_dir/chi2_distribution.pdf",facecolor='white',edgecolor='white')

## Function to get the size of the terminal
#
# Reads the width and height of the current terminal and returns
# this two values.
# @param[out] int(cr[1]) Width of the terminal
# @param[out] int(cr[0]) Height of the terminal
def getTerminalSize():
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])

## Function to create and update a progress bar
#
# This function displays or updates a console progress bar
# It accepts a float between 0 and 1. Any int will be converted to a float.
# A value under 0 represents a 'halt'.
# A value at 1 or bigger represents 100%
# @param[in] progress Relative progress that should be displayed
def update_progress(progress):
    (width, height) = getTerminalSize()
    barLength = width-30 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = bcolors.FAIL+"error: progress var must be float\r\n"+bcolors.ENDC
    if progress < 0:
        progress = 0
        status = bcolors.WARNING+"Halt...\r\n"+bcolors.ENDC
    if progress >= 1:
        progress = 1
        status = bcolors.OKGREEN+"Done...\r\n"+bcolors.ENDC
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( bcolors.HEADER+"#"*block+bcolors.ENDC + "-"*(barLength-block), int(progress*100), status)
    sys.stdout.write(text)
    sys.stdout.flush()

def make_comparison_plot(i):
    sample = i[0]
    folder = i[1]
    key = i[2]
    hist = key[key.find(folder)+len(folder)+1:]
    log.debug("Now plotting: " +folder+"/"+hist + " from: comparison_dir/old/%s.root"%(sample))
    comp_file = TFile("comparison_dir/old/%s.root"%(sample),"READ")
    ref_hist = TH1F()
    ref_hist = comp_file.Get(folder+"/"+hist)
    ref_hist.SetDirectory(0)
    ref_hist.SetLineColor(ro.kGreen)
    comp_file.Close()
    new_file = TFile("comparison_dir/new/%s.root"%(sample),"READ")
    new_hist = TH1F()
    new_hist = new_file.Get(folder+"/"+hist)
    new_hist.SetDirectory(0)
    new_hist.SetLineColor(ro.kRed)
    new_file.Close()

    if ref_hist.GetNbinsX() > 500:
        ref_hist.Rebin(10)
        new_hist.Rebin(10)

    if not i[3].allplots:
        if ref_hist.GetEntries() == 0 and new_hist.GetEntries() == 0:
            return ["NONE",0.0]

    chi2 = Chi2_calcer(ref_hist,new_hist)

    temp_x_vals = []
    temp_x_err = []
    temp_y_vals = []
    temp_y_err = []
    temp_new_x_vals = []
    temp_new_x_err = []
    temp_new_y_vals = []
    temp_new_y_err = []
    temp_ratio = []
    temp_ratio_err = []
    temp_sig = []
    temp_sig_err = []
    range_x_vals = []
    range_y_vals = []
    for j in range(1,ref_hist.GetNbinsX()+1):
        temp_x_vals.append(ref_hist.GetBinCenter(j))
        temp_x_err.append(ref_hist.GetBinWidth(j)/2.)
        temp_y_vals.append(ref_hist.GetBinContent(j))
        if ref_hist.GetBinContent(j) != 0.0:
            range_x_vals.append(ref_hist.GetBinCenter(j))
            range_y_vals.append(ref_hist.GetBinContent(j))
        temp_y_err.append(ref_hist.GetBinError(j))
        temp_new_x_vals.append(new_hist.GetBinCenter(j))
        temp_new_x_err.append(new_hist.GetBinWidth(j)/2.)
        temp_new_y_vals.append(new_hist.GetBinContent(j))
        if new_hist.GetBinContent(j) != 0.0:
            range_x_vals.append(new_hist.GetBinCenter(j))
            range_y_vals.append(new_hist.GetBinContent(j))
        temp_new_y_err.append(new_hist.GetBinError(j))
        if ref_hist.GetBinContent(j) != 0.0:# and new_hist.GetBinContent(j) != 0.0:
            temp_ratio.append(temp_new_y_vals[-1]/temp_y_vals[-1])
            temp_ratio_err.append(sqrt(pow(temp_new_y_err[-1]/temp_y_vals[-1],2) + pow(temp_new_y_vals[-1]*temp_y_err[-1]/temp_y_vals[-1]/temp_y_vals[-1],2)))
            temp_sig.append((temp_new_y_vals[-1] - temp_y_vals[-1]) / sqrt(pow(temp_new_y_err[-1],2) + pow(temp_y_err[-1],2)))
            temp_sig_err.append(1.)
        else:
            temp_ratio.append(0.)
            temp_ratio_err.append(0.)
            temp_sig.append(0.)
            temp_sig_err.append(0.)
    if len(range_x_vals) < 1:
        range_x_vals.append(0)
        range_x_vals.append(1)
    if len(range_y_vals) < 1:
        range_y_vals.append(0)
        range_y_vals.append(1)
    fig = plt.figure(figsize=(8, 10), dpi=20, facecolor='white')
    ax = fig.add_subplot(3,1,1,axisbg='white')
    make_axis(ax,"$"+ref_hist.GetXaxis().GetTitle().replace("#","\\")+"$","$Events$","")
    ax.set_yscale("symlog")
    log.debug(hist + ":   " + str((np.min(range_y_vals) - 1)*0.8) +"  "+ str((np.max(range_y_vals) + 1)*1.2))
    plt.xlim( np.min(range_x_vals)*0.95, np.max(range_x_vals)*1.05 )
    plt.ylim( (np.min(range_y_vals) - 1)*0.95, (np.max(range_y_vals) + 1)*1.05 )
    plt.errorbar(temp_x_vals, temp_y_vals, xerr = temp_x_err, yerr = temp_y_err, color='chartreuse',marker="o",linestyle="-",linewidth=1,label='Reference')
    plt.errorbar(temp_new_x_vals, temp_new_y_vals, xerr = temp_new_x_err, yerr = temp_new_y_err, color='red',marker="o",linestyle="-",linewidth=1,label='New (for validation)')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)

    text = ax.text(0.8, 0.9, 'chi2/Ndf: %.2f'%(chi2), color='limegreen', transform=ax.transAxes,
                va='bottom', ha='center')

    ax = fig.add_subplot(3,1,2,axisbg='white')
    make_axis(ax,"$"+ref_hist.GetXaxis().GetTitle().replace("#","\\")+"$","$(N_{events}^{new} - N_{events}^{old}) / \sigma$","")
    plt.xlim( np.min(range_x_vals)*0.95, np.max(range_x_vals)*1.05 )
    plt.errorbar(temp_new_x_vals, temp_sig, xerr = temp_new_x_err, yerr = temp_sig_err, color='y',marker="o",linestyle="-",linewidth=1)

    ax = fig.add_subplot(3,1,3,axisbg='white')
    make_axis(ax,"$"+ref_hist.GetXaxis().GetTitle().replace("#","\\")+"$","$N_{events}^{new} / N_{events}^{old}$","")
    plt.xlim( np.min(range_x_vals)*0.95, np.max(range_x_vals)*1.05 )
    plt.errorbar(temp_new_x_vals, temp_ratio, xerr = temp_new_x_err, yerr = temp_ratio_err, color='y',marker="o",linestyle="-",linewidth=1)

    name = "comparison_dir/" + sample + "_" + folder + "_" + hist + ".pdf"
    plt.show()
    plt.savefig(name,facecolor='white',edgecolor='white')
    return [name,chi2]

def make_output_file(sample_list,cfg_file,options):
    control_output("Creating the summary file",True,True)

    content = r'''\documentclass[12pt]{article}
\usepackage{amsmath}    % need for subequations
\usepackage{graphicx}   % need for figures
\usepackage{verbatim}   % useful for program listings
\usepackage{color}      % use if color is used in text
\usepackage{subfigure}  % use for side-by-side figures
\usepackage{hyperref}   % use for hypertext links, including those to external documents and URLs
\usepackage{morefloats}
\definecolor{darkgreen}{rgb}{0,0.5,0.1}

% above is the preamble

\begin{document}'''

    content = create_tex_summary(content,sample_list,cfg_file,options)

    content += r'''
\end{document}
'''
    content = content.replace("_","\_")
    content = content.replace("!","_")
    tex_file = open("test.tex","w")
    tex_file.write(content)
    tex_file.close()

    log.debug("Compiling .tex document")
    p = subprocess.Popen("pdflatex test.tex",shell=True,stdout=subprocess.PIPE)
    output = p.communicate()[0]
    log.debug(output)

    log.debug("Second compilation of .tex file")
    p1 = subprocess.Popen("pdflatex test.tex",shell=True,stdout=subprocess.PIPE)
    output = p1.communicate()[0]
    log.debug(output)

    log.debug("done. Now cleaning up")
    p2 = subprocess.Popen("rm test.tex test.toc test.aux test.log test.out",shell=True,stdout=subprocess.PIPE)
    output = p2.communicate()[0]
    log.debug(output)
    log.debug("done")

def Chi2_calcer(hist1,hist2):
    if hist1.GetEntries() == 0 and hist2.GetEntries() == 0:
        return 0.0
    elif hist1.GetEntries() == 0:
        return float(hist2.GetEntries())/hist2.GetNbinsX()
    elif hist2.GetEntries() == 0:
        return float(hist1.GetEntries())/hist1.GetNbinsX()
    else:
        return hist1.Chi2Test(hist2,"WW CHI2/NDF")

def main():
    t0 = time.time()
    control_output("doing the validation",True,True)

    args,options,cfg_file = opt_parser()

    sample_list = get_sample_list(cfg_file)

    run_analysis(options,cfg_file,sample_list)

    get_analysis_output(options)

    get_reference_output(options)

    do_comparison(options,cfg_file,sample_list)

    make_output_file(sample_list,cfg_file,options)

    decision = final_user_decision()

    if decision == True:
        make_new_reference()

        authorization = check_authorization()

        if authorization == True:
            make_commits()
    t1 = time.time()
    print("\n \t Runtime: %.2f s"%(t1-t0))

if __name__ == '__main__':
    main()
