# chronoamp script #


#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

#---Clear mac terminal memory---#
import os
import matplotlib
matplotlib.use('TkAgg')
os.system("clear && printf '\e[3J'")

#---Import Modules---#
import sys
import time as t
import datetime
try:
    import Tkinter as tk
    from Tkinter.ttk import *
    from Tkinter import *
    from Tknter import filedialog

except ImportError: # Python 3
    import tkinter as tk
    from tkinter.ttk import *
    from tkinter import *
    from tkinter import filedialog

from matplotlib import style
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.patches import Polygon
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import numpy as np
import csv
from pylab import *
from numpy import *
from scipy.interpolate import *
from scipy.integrate import simps
from scipy.optimize import curve_fit
from scipy.signal import *
from itertools import *
import math
from math import log10, floor
from decimal import Decimal
from operator import truediv
import threading
from threading import Thread, Event
from collections import Counter
from queue import Queue
style.use('ggplot')

#---Filter out error warnings---#
import warnings
warnings.simplefilter('ignore', np.RankWarning)         #numpy polyfit_deg warning
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd") #RuntimeWarning


#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

handle_variable = ''
#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

                                ########################
                                ### Global Variables ###
                                ########################

Interval = 100
file_limit = 52
point_limit = 20
short_aa = 10**(-3)         # points removed from the the beginning of the short pulse
short_zz = 10**(-2)         # points removed from the the end of the short pulse
long_aa = 10**(-2)            # points removed from the the beginning of the long pulse
long_zz = 1                # points removed from the the end of the long pulse

AlreadyInitiated = False

#--- Styling ---#
HUGE_FONT = ('Verdana', 18)
LARGE_FONT = ('Verdana', 12)
MEDIUM_FONT = ('Verdnana', 10)
SMALL_FONT = ('Verdana', 8)


#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#



#############################################
### Class that contains all of the frames ###
#############################################
class RealTimeAnalysis(tk.Tk):

    #--- Initialize the GUI ---#
    def __init__(self, *args, **kwargs):
        global container, PlotContainer, fig, ax, ShowFrames

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self,'Real-Time E-AB Sensing Platform')
        tk.Tk.resizable(self,width=False, height=False)             ## make the window size static

        #--- Create a frame for the UI ---#
        container = tk.Frame(self,relief='flat',bd=5).grid(row=0,column=0,padx=5,sticky='nsw')

        #--- Raise the frame for initial UI ---#
        ShowFrames = {}                                 # Key: frame handle / Value: tk.Frame object
        frame = StartPage(container, self)
        ShowFrames[StartPage] = frame
        frame.grid(row=0, column=0, sticky='nsw')
        self.show_frame(StartPage)


    #--- Function to visualize different frames ---#
    def show_frame(self, cont):

        frame = ShowFrames[cont]
        frame.tkraise()


    def show_plot(self, frame):
        frame.tkraise()


#--- Frame for User Input ---#
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        global point_limit_variable, file_limit_entry, point_limit_entry

        tk.Frame.__init__(self, parent)             # initialize the frame

        self.SelectFilePath = ttk.Button(self, style = 'Off.TButton', text = 'Select File Path', command = lambda: self.FindFile(parent))
        self.SelectFilePath.grid(row=0,column=0,columnspan=3)

        self.NoSelectedPath = tk.Label(self, text = 'No File Path Selected', font = MEDIUM_FONT, fg = 'red')
        self.PathWarningExists = False               # tracks the existence of a warning label

        ImportFileLabel = tk.Label(self, text = 'Data File Handle', font=LARGE_FONT).grid(row=2,column=0,columnspan=3)
        self.ImportFileEntry = tk.Entry(self)
        self.ImportFileEntry.grid(row=3,column=0,columnspan=3,pady=5)
        self.ImportFileEntry.insert(END, handle_variable)

        #--- File Handle Input ---#
        HandleLabel = tk.Label(self, text='Exported File Handle:', font=LARGE_FONT)
        HandleLabel.grid(row=4,column=0,columnspan=3)
        self.filehandle = ttk.Entry(self)
        now = datetime.datetime.now()
        hour = str(now.hour)
        day = str(now.day)
        month = str(now.month)
        year = str(now.year)
        self.filehandle.insert(END, 'DataExport_%s_%s_%s.txt' % (year, month, day))
        self.filehandle.grid(row=5,column=0,columnspan=3,pady=5)

        file_limit_label = tk.Label(self, text='Enter File Limit',font=LARGE_FONT)
        file_limit_label.grid(row=7,column=0,columnspan=3)

        file_limit_entry = tk.Entry(self, width=10)
        file_limit_entry.insert(END, str(file_limit))
        file_limit_entry.grid(row=10,column=0,columnspan=3)

        point_limit_label = tk.Label(self, text='Enter Number of Points to Average', font=LARGE_FONT)
        point_limit_label.grid(row=15,column=0,columnspan=3)

        point_limit_entry = tk.Entry(self, width=10)
        point_limit_entry.insert(END, str(point_limit))
        point_limit_entry.grid(row=20,column=0,columnspan=3)

        start_button = ttk.Button(self, text = 'Initiate Visualization', command = self.StartProgram).grid(row=25,column=0,columnspan=3,pady=5,padx=5)
        quit_button = tk.Button(self, text = 'Quit', command = lambda: quit()).grid(row=30,column=0,columnspan=3,pady=5,padx=5)

        #--- Ask the User if they want to export the data to a .txt file ---#
        self.SaveVar = BooleanVar()
        self.SaveVar.set(False)
        self.SaveBox = Checkbutton(self, variable=self.SaveVar, onvalue=True, offvalue=False, text="Export Data").grid(row=35,column=0,columnspan=3)


    def FindFile(self, parent):
        global mypath, ExportPath, FoundFilePath, NoSelectedPath

        try:

            ### prompt the user to select a  ###
            ### directory for  data analysis ###
            mypath = filedialog.askdirectory(parent = parent)
            mypath = ''.join(mypath + '/')


            ### Path for directory in which the    ###
            ### exported .txt file will be placed  ###
            ExportPath = mypath.split('/')

            #-- change the text of the find file button to the folder the user chose --#
            DataFolder = '%s/%s' % (ExportPath[-3],ExportPath[-2])

            self.SelectFilePath['style'] = 'On.TButton'
            self.SelectFilePath['text'] = DataFolder



            del ExportPath[-1]
            del ExportPath[-1]
            ExportPath = '/'.join(ExportPath)
            ExportPath = ''.join(ExportPath + '/')
            print(ExportPath)

            ## Indicates that the user has selected a File Path ###
            FoundFilePath = True

            if self.PathWarningExists:
                self.NoSelectedPath['text'] = ''
                self.NoSelectedPath.grid_forget()

        except:
            print('\n\nInputPage.FindFile: Could Not Find File Path\n\n')



    def StartProgram(self):
        global initiate_figures, FileHandle, PlotContainer, handle_variable, export_data, SaveVar

        #--- Initiate the Frame for Data Visualization ---#
        initiate_figures = InitiateFigures()
        handle_variable = self.ImportFileEntry.get()
        SaveVar = self.SaveVar.get()
        FileHandle = self.filehandle.get()


        export_data = TextFileExport()


        FileHandle = str(self.filehandle.get()) # handle for exported .txt file
        FileHandle = ''.join(ExportPath + FileHandle)
        print('FileHandle',FileHandle)

        ##############################################################################
        ### Frame for Real-Time User Input for Data Manipulation and Visualization ###
        ##############################################################################
        class RealTimeInputFrame(tk.Frame):

            def __init__(self, parent, controller):
                global pulse_label, file_label

                tk.Frame.__init__(self, parent)          # initiate the Frame

                file_header = tk.Label(self,text = 'File Number',font=LARGE_FONT)
                file_header.grid(row=0,column=0,ipady=5,pady=5,ipadx=5,padx=5,)
                file_label = ttk.Label(self, text = '1', font=LARGE_FONT, style='Fun.TButton')
                file_label.grid(row=1,column=0,padx=10,ipadx=10)

                pulse_header = tk.Label(self, text= 'Point Number',font=LARGE_FONT)
                pulse_header.grid(row=0,column=1,ipady=5,pady=5,ipadx=5,padx=5)
                pulse_label = ttk.Label(self, text = '1', font=LARGE_FONT, style='Fun.TButton')
                pulse_label.grid(row=1,column=1,padx=10,ipadx=10)


                #######################################################################
                ### Real-Time adjustment of points discarded at beginning of pulses ###
                #######################################################################
                RegressionFrame = tk.Frame(self,relief='groove',bd=5)
                RegressionFrame.grid(row=2,column=0,columnspan=4,pady=5,padx=5,ipadx=3)

                #--- Title ---#
                self.RegressionLabel = tk.Label(RegressionFrame, text = 'Regression Analysis Parameters', font=LARGE_FONT)
                self.RegressionLabel.grid(row=0,column=0,columnspan=4,pady=5,padx=5)

                #--- Create frames to hold parameters for short and long pulses, respectively ---#
                self.ShortParameterFrame = tk.Frame(RegressionFrame,relief='groove',bd=2)             # Frame to hold the parameters for frequencies <= 50Hz
                self.ShortParameterFrame.grid(row=1,column=0,columnspan=4)
                self.LongParameterFrame = tk.Frame(RegressionFrame,relief='groove',bd=2)            # Frame to hold the parameters for frequencies > 50Hz
                self.LongParameterFrame.grid(row=1,column=0,columnspan=4)

                #--- Buttons to switch in between long and short pulse parameter frames ---#
                self.SelectShortParameters = ttk.Button(RegressionFrame, text = 'Short Parameters', style = 'Off.TButton', command = lambda: self.SwitchParameterFrame('Short'))
                self.SelectShortParameters.grid(row=2,column=0,pady=5,padx=5,sticky='nsew')
                self.SelectLongParameters = ttk.Button(RegressionFrame, text = 'Long Parameters', style = 'On.TButton', command = lambda: self.SwitchParameterFrame('Long'))
                self.SelectLongParameters.grid(row=2,column=1,pady=5,padx=5,sticky='nsew')

                ##################################################################################
                ### Parameters for points discarded at the beginning and end of the short pulse ###
                ##################################################################################
                #--- Title ---#
                self.ShortLabel = tk.Label(self.ShortParameterFrame, text = 'Short Pulse Parameters', font=MEDIUM_FONT).grid(row=0,column=0,columnspan=2)

                #--- points discarded at the beginning of pulse ---#
                self.short_aa_label = tk.Label(self.ShortParameterFrame, text = 'short_aa (s)', font=MEDIUM_FONT).grid(row=1,column=0)
                self.short_aa_entry = tk.Entry(self.ShortParameterFrame, width=7)
                self.short_aa_entry.insert(END, str(short_aa))
                self.short_aa_entry.grid(row=2,column=0)
                short_aa_entry = self.short_aa_entry

                #--- points discarded at the end of the pulse ---#
                self.short_zz_label = tk.Label(self.ShortParameterFrame, text = 'short_zz (s)', font=MEDIUM_FONT).grid(row=1,column=1)
                self.short_zz_entry = tk.Entry(self.ShortParameterFrame, width=7)
                self.short_zz_entry.insert(END, str(short_zz))
                self.short_zz_entry.grid(row=2,column=1)
                short_zz_entry = self.short_zz_entry

                ##################################################################################
                ### Parameters for points discarded at the beginning and end of the long pulse ###
                ##################################################################################
                #--- Frame Title ---#
                self.LongLabel = tk.Label(self.LongParameterFrame, text = 'Long Pulse Parameters', font=MEDIUM_FONT).grid(row=0,column=0,columnspan=2)

                #--- points discarded at the beginning of the pulse ---#
                self.long_aa_label = tk.Label(self.LongParameterFrame, text = 'long_aa (s)', font=MEDIUM_FONT).grid(row=1,column=0)
                self.long_aa_entry = tk.Entry(self.LongParameterFrame, width=7)
                self.long_aa_entry.insert(END, str(long_aa))
                self.long_aa_entry.grid(row=2,column=0)
                long_aa_entry = self.long_aa_entry

                #--- points discarded at the end of the pulse ---#
                self.long_zz_label = tk.Label(self.LongParameterFrame, text = 'long_zz (s)', font=MEDIUM_FONT).grid(row=1,column=1)
                self.long_zz_entry = tk.Entry(self.LongParameterFrame, width=7)
                self.long_zz_entry.insert(END, str(long_zz))
                self.long_zz_entry.grid(row=2,column=1)
                long_zz_entry = self.long_zz_entry

                #--- Button to apply adjustments ---#
                self.AdjustParameterButton = tk.Button(RegressionFrame, text = 'Apply Adjustments', font=LARGE_FONT, command = lambda: self.AdjustParameters())
                self.AdjustParameterButton.grid(row=3,column=0,columnspan=4,pady=10,padx=10)

                #################################################################
                ### Frame for determining real-time bounds of exponential fit ###
                #################################################################
                self.ExponentialFitParameterFrame = tk.Frame(self, bd=5, relief='groove')                      # container
                self.ExponentialFitParameterFrame.grid(row=3,column=0,columnspan=3,pady=5)

                self.ExponentialFrameLabel = tk.Label(self.ExponentialFitParameterFrame, text = 'Curve Fit Range').grid(row=0,column=0,columnspan=2,pady=5)

                self.Exponential_LowLabel = tk.Label(self.ExponentialFitParameterFrame, text = 'Lower Limit (ms)', font = MEDIUM_FONT).grid(row=1,column=0)
                self.Exponential_LowLimit = tk.Entry(self.ExponentialFitParameterFrame, width=7)
                self.Exponential_LowLimit.grid(row=2,column=0)
                self.Exponential_LowLimit.insert(END, 4)

                self.Exponential_HighLabel = tk.Label(self.ExponentialFitParameterFrame, text = 'Higher Limit (ms)', font = MEDIUM_FONT).grid(row=1,column=1)
                self.Exponential_HighLimit = tk.Entry(self.ExponentialFitParameterFrame, width=7)
                self.Exponential_HighLimit.grid(row=2,column=1)
                self.Exponential_HighLimit.insert(END, 110)

                self.ApplyExponentialParameters = tk.Button(self.ExponentialFitParameterFrame, text = 'Apply Adjustments',command = lambda: self.ApplyExponentialAdjustments())
                self.ApplyExponentialParameters.grid(row=3,column=0,columnspan=2,pady=5)

                ###############################
                ### Start and Reset Buttons ###
                ###############################
                self.StartButton = tk.Button(self, text = 'Begin Visualization', command = lambda: self.StartProgram()).grid(row=4,column=0,pady=5)
                self.ResetButton = tk.Button(self, text = 'Reset', command = lambda: self.Reset()).grid(row=4,column=1,pady=5)


            #--- Real-Time Adjustment of visualization parameters ---#
            def AdjustParameters(self):
                #--- Adjusts the parameters used to visualize the raw voltammogram, smoothed currents, and polynomial fit
                global short_aa, long_aa, short_zz, long_zz

                #--- parameters for short pulse ---#
                short_aa = float(self.short_aa_entry.get())               # aa/zz adjust the points at the start and end of the polynomial fit, respectively
                short_zz = float(self.short_zz_entry.get())

                #--- parameters for long pulse ---#
                long_aa = float(self.long_aa_entry.get())
                long_zz = float(self.long_zz_entry.get())

            def SwitchParameterFrame(self, frame):

                if frame == 'Short':
                    self.ShortParameterFrame.tkraise()

                    self.SelectShortParameters['style'] = 'On.TButton'
                    self.SelectLongParameters['style'] = 'Off.TButton'

                if frame == 'Long':
                    self.LongParameterFrame.tkraise()

                    self.SelectShortParameters['style'] = 'Off.TButton'
                    self.SelectLongParameters['style'] = 'On.TButton'

            def ApplyExponentialAdjustments(self):
                global exp_high, exp_low

                exp_low = (int(self.Exponential_LowLimit.get()))/1000       # msec --> sec
                exp_high = (int(self.Exponential_HighLimit.get()))/1000

            def StartProgram(self):
                global chronoamperometry_analysis, AlreadyInitiated, exp_low, exp_high

                AlreadyInitiated = True

                exp_low = int(self.Exponential_LowLimit.get())/1000
                exp_high = int(self.Exponential_HighLimit.get())/1000

                #--- begin the animation of the chronoamperometry data ---#
                chronoamperometry_analysis = ChronoamperometryAnalysis()


            #--- Function to Reset and raise the user input frame ---#
            def Reset(self):
                global PoisonPill, ThreadQueue

                if AlreadyInitiated:
                    PoisonPill.set()

                    chronoamperometry_analysis.Reset()

                self.close_frame(RealTimeInputFrame)
                self.show_frame(StartPage)

            def show_frame(self, cont):

                frame = ShowFrames[cont]
                frame.tkraise()

            def close_frame(self, cont):

                frame = ShowFrames[cont]
                frame.grid_forget()

                PlotContainer.destroy()


        #--- Initiate the Real-Time User Input Frame ---#
        RT_InputFrame = RealTimeInputFrame(container, self)
        RT_InputFrame.grid(row=0,column=0,sticky='nsw')
        ShowFrames[RealTimeInputFrame] = RT_InputFrame
        RT_InputFrame.tkraise()



########################################################
### Create the figures and axes for the loglog plots ###
########################################################
class InitiateFigures():
    def __init__(self):
        global figures, container, PlotContainer

        figures = {}    # global figure and axes list

        #--- create a figure and axes that will render the data ---#
        self.MakeFigure()

        class PlotContainer(tk.Frame):
            def __init__(self, parent, controller):

                tk.Frame.__init__(self, parent)             # initialize the frame

        #--- Create a container that can be created and destroyed when Start() or Reset() is called, respectively ---#
        PlotContainer = PlotContainer(container, self)
        PlotContainer.relief = 'flat'
        PlotContainer.grid(row=0,column=1)

        ###############################################################
        ### Class for creating instances of the visualization frame ###
        ###############################################################
        class VisualizationFrame(tk.Frame):

            def __init__(self, parent, controller):
                tk.Frame.__init__(self, parent)         # Initialize the frame

                #--- Voltammogram, Raw Peak Height, and Normalized Figure and Artists ---#
                fig = figures['figure']
                canvas = FigureCanvasTkAgg(fig, self)                                         # and place the artists within the frame
                canvas.draw()                                                                 # initial draw call to create the artists that will be blitted
                canvas.get_tk_widget().grid(row=2,padx=5,pady=6,ipady=5)         # does not affect size of figure within plot container


        FrameReference = VisualizationFrame(PlotContainer, self)
        FrameReference.grid(row=0,column=0)
        FrameReference.tkraise()

    def MakeFigure(self):
        global figures

        fig, ax = plt.subplots(nrows=1,ncols=2)
        plt.subplots_adjust(bottom=0.1,hspace=0.6,wspace=0.3)         ### adjust the spacing between subplots

        #-- set the limits of the loglog axes ---#
        ax[0].set_ylim(5*10**-9,10**-4)           # Amperes
        ax[0].set_xlim(4*10**-4,5*10**-1)         # seconds

        ax[0].set_ylabel('Current (A)',fontweight='bold')
        ax[0].set_xlabel('Time (s)',fontweight='bold')

        #-- set the chronoamperogram to a loglog scale
        ax[0].set_yscale('log')
        ax[0].set_xscale('log')

        #--- create a plot for Fitted Half life v File Number
        ax[1].set_ylim(0,15)                                    # Half Life
        ax[1].set_xlim(0,int(file_limit_entry.get())+0.1)      # File Number

        ax[1].set_ylabel('Half Life (ms)',fontweight='bold')
        ax[1].set_xlabel('File Number',fontweight='bold')

        figures['figure'] = fig
        figures['axes'] = ax

        print('Made Figures')





#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#




#############################################
### Data Analysis and Visualization class ###
#############################################
class ChronoamperometryAnalysis():
    def __init__(self):
        global anim

        self.initialize()

        #########################################
        ### Create a thread for Data Analysis ###
        #########################################

        anim = []
        self.anim = ThreadedAnimation(figures['figure'], self.animate, generator=self.frames(), interval=Interval)

        anim.append(self.anim)

    ####################################################################
    ### Analze the first file to retrieve the experiments parameters ###
    ### and create a dictionary containing their values              ###
    ####################################################################
    def initialize(self):
        global anim, ParameterPipe

        self.file = 1
        self.index = 1

        self.exp_low = exp_low
        self.exp_high = exp_high

        self.ParameterPipe = Queue()
        ParameterPipe = self.ParameterPipe

        self.volt_dict = {}     # dictionary for voltage parameters

        self.short_dict = self.get_parameters('short')
        self.long_dict = self.get_parameters('long')

        self.file_limit = int(file_limit_entry.get())
        self.point_limit = int(point_limit_entry.get())

        ### create a list to hold lifetime values
        self.lifetime_list = []
        self.fitted_lifetime_list = []

        ### prepare figures and artists to be visualized
        self.prepare_figure()

    def Reset(self):

        self.file = 1

    ######################################
    ### Create artists for each figure ###
    ### 1. raw exponential decay       ###
    ### 2. fitted exponential decay    ###
    ### 3. extrapolated lifetime (ms)  ###
    ######################################
    def prepare_figure(self):
        global plots

        #--- create a primtive artist that will contain the visualized data ---#
        ax = figures['axes']

        # Data Artists
        self.raw_decay, = ax[0].plot(1,1, 'ko', MarkerSize=1)        # loglog amperogram
        self.curve_fit, = ax[0].plot(1,1, 'r-', MarkerSize=1)   # loglog curve fit
        self.fitted_lifetime, = ax[1].plot(0,0, ' bo', MarkerSize=1) # fitted lifetime (ms)

        # empty arists for empty init functions
        self.EmptyPlots, = ax[0].plot(1,1, 'ro', MarkerSize=1)

        plots = {}
        plots['line'] = self.raw_decay        # global reference
        plots['curve fit'] = self.curve_fit
        plots['fitted lifetime'] = self.fitted_lifetime
        plots['EmptyPlots'] = self.EmptyPlots

    ### Analyze the first file and extrapolate parameters ###
    ### 1. voltage_1: 1st potential step (int; V)
    ### 2. voltage_2: 2nd potential step (int; V)
    ### 3. pulse_width: width of voltage_1 (int; V)
    ### 4. sample_rate: sample rate (int; s)
    ### 5. variables: # of points per pulse (int)
    def get_parameters(self, pulse):

        # dicionary for voltage parameters #

        if pulse == 'short':
            filehandle = 'Short_%s_#1_#1.DTA' % handle_variable
        elif pulse == 'long':
            filehandle = 'Long_%s_#1_#1.DTA' % handle_variable

        myfile = mypath + filehandle

        try:
            mydata_bytes = os.path.getsize(myfile)    ### retrieves the size of the file in bytes
        except:
            mydata_bytes = 1

        #---if the file meets the size requirement, analyze data---#
        if mydata_bytes > 1000:

            #---Preallocate Potential and Current lists---#
            with open(myfile,'r',encoding='utf-8') as mydata:
                voltages = []
                dictionary = {}
                val = 0
                for line in mydata:
                    line = ' '.join(line.split())
                    line = line.strip()

                    #--- Step One Potential ---#
                    if line.startswith('VSTEP1'):
                        voltage_1 = ' '.join(line.split())          # remove repeated white space
                        voltage_1 = voltage_1.split(' ')            # then separate each string
                        voltage_1 = voltage_1[2]                    # and grab the potential from the 3rd column
                        volt_1 = voltage_1
                        voltage_1 = voltage_1.split('E')
                        exponent = voltage_1[1]
                        voltage_1 = voltage_1[0]
                        voltage_1 = float(voltage_1) * (10**float(exponent))
                        self.volt_dict[voltage_1] = volt_1

                    #--- Step Two Potential ---#
                    if line.startswith('VSTEP2'):
                        voltage_2 = ' '.join(line.split())
                        voltage_2 = voltage_2.split(' ')
                        voltage_2 = voltage_2[2]
                        volt_2 = voltage_2
                        voltage_2 = voltage_2.split('E')
                        exponent = voltage_2[1]
                        voltage_2 = voltage_2[0]
                        voltage_2 = float(voltage_2) * (10**float(exponent))
                        self.volt_dict[voltage_2] = volt_2

                    #--- Step One Pulse Width ---#
                    if line.startswith('TSTEP1'):
                        pulse_width = ' '.join(line.split())
                        pulse_width = pulse_width.split(' ')
                        pulse_width = pulse_width[2]
                        pulse_width = pulse_width.split('E')
                        exponent = pulse_width[1]
                        pulse_width = pulse_width[0]
                        pulse_width = float(pulse_width) * (10**float(exponent))
                        dictionary['pulse width'] = pulse_width

                    #--- Sample Rate ---#
                    if line.startswith('SAMPLETIME'):
                        sample_rate = ' '.join(line.split())
                        sample_rate = sample_rate.split(' ')
                        sample_rate = sample_rate[2]

                        sample_rate = sample_rate.split('E')
                        exponent = sample_rate[1]
                        sample_rate = sample_rate[0]
                        sample_rate = float(sample_rate) * (10**float(exponent))
                        dictionary['sample period'] = sample_rate

                    val += 1

            #--- extrapolate the number of files in one pulse ---#
            variables = math.ceil(int((pulse_width/sample_rate)))
            dictionary['variables'] = variables

            #--- extrapolate the reduction potential --#
            reduction_voltage = max(abs(voltage_1),abs(voltage_2))            # reduction voltage
            if voltage_1 < 0:
                reduction_voltage = reduction_voltage * -1
            dictionary['reduction voltage'] = reduction_voltage

            return dictionary

        ### If the file has not been found, keep searching
        else:
            print('could not initialize')
            root.after(200, self.initialize)

    ####################################################################
    ### Using the data provided, calculate the lifetime of the decay ###
    ####################################################################
    def set_fit(self, time_data, current_data):

        A1, C1, K1, A2, C2, K2, adjusted_time, adjusted_currents = self.extract_parameters(time_data, current_data)

        popt, pcov = curve_fit(self.biexponential_func, adjusted_time, adjusted_currents, p0 = (A1, K1, A2, K2))

        return popt, pcov, C2


    def extract_parameters(self, time_data, current_data):

        zip_list = sorted(set(zip(time_data, current_data)))

        # create a key,value dictionary with format {current: time}
        initial_dict = {}
        for item in zip_list:
            time, current = item
            initial_dict[time] = current

        ## Adjust the time data to fit the parameters set by the user
        try:
            adjusted_time = [time for time in time_data if exp_low <= time <= exp_high]
        except:
            print('\nCould not apply exponential adjustments to time data\n')

        ## create a new dictionary that will correlate
        ## the currents to the adjusted time_data
        adjusted_currents = []
        adjusted_dict = {}
        for item in zip_list:
            time, current = item
            if time in adjusted_time:
                adjusted_currents.append(current)
                adjusted_dict[current] = time

        ###########################
        ### Monoexponential Fit ###
        ###########################

        ### get a initial assumption for the A value in y = Ae^(-kt) + C
        initial_A = adjusted_currents[5]

        ### get an initial assumption for the C value in y = Ae^(-kt) + C
        initial_C = adjusted_currents[-5]

        ### get the y value for the half-life
        half_life = 0.33*(float(initial_A))

        ### find the closest real value to the theoretical half life
        closest_current = min(adjusted_currents, key = lambda x:abs(x-half_life))
        closest_time = adjusted_dict[closest_current]

        ## linearize both sides  with the natural log and extrapolate K
        ## in exponential equation y = Ae^(-kt) + C
        initial_K = (math.log(initial_A) - math.log(closest_current - initial_C))/closest_time

        ### Separate the data into two zip files to ###
        ### fit to a biexponential function         ###

        half = math.ceil(0.5 * len(adjusted_time))

        decay_1 = sorted(set(zip(adjusted_time[:half],adjusted_currents[:half])))
        decay_2 = sorted(set(zip(adjusted_time[half:],adjusted_currents[half:])))
        A1, C1, K1 = self.extract_fit(decay_1)
        A2, C2, K2 = self.extract_fit(decay_2)

        return A1, C1, K1, A2, C2, K2, adjusted_time, adjusted_currents
        ### Get initial parameters for each decay ###


        ## return a parameters fitted to the curve with a minimization function
        ## and based upon the suggestion of the variables p0

    ### Curve is a zip list of (time, current)
    def extract_fit(self, curve):

        try:
            time_data = []
            currents = []
            dict = {}

            for item in curve:
                time, current = item
                time_data.append(time)
                currents.append(current)
                dict[current] = time

            ### get a initial assumption for the A value in y = Ae^(-kt) + C
            A = currents[5]
            print('Initial Amplitude:',A)

            ### get an initial assumption for the C value in y = Ae^(-kt) + C
            C = currents[-20]
            print('Initial Constant:',C)
            self.constant = C

            ### get the y value for the half-life
            half_life = 0.33*(float(A))

            ### find the closest real value to the theoretical half life
            closest_current = min(currents, key = lambda x:abs(x-half_life))
            closest_time = dict[closest_current]

            ## linearize both sides  with the natural log and extrapolate K
            ## in exponential equation y = Ae^(-kt) + C
            try:
                K = (math.log(A) - math.log(closest_current - C))/closest_time
            except:
                K = (math.log(A) - math.log(closest_current))/closest_time

            print('\nExtract Fit: Time Constant', K)

            return A, C, K
        except:
            print('couldt perform extraction')

    #######################
    ### Monoexponential ###
    #######################
    def exponential_func(self, t, a, k, c):
        return (a * np.exp(-t * k) + c)

    #####################
    ### Biexponential ###
    #####################
    def biexponential_func(self, t, a, b, c, d, e = None):

        if e is None:
            e = self.constant

        return a * np.exp(-t * b) + c * np.exp(-t * d) + e

    ###############################################
    ### Generator Function for data acquisition ###
    ###############################################
    def frames(self):
        global file_label, plots, ThreadQueue

        while True:
            while self.file <= self.file_limit:

                self.file = ThreadQueue.get()

                print('File Recieved from Queue: %s' % str(self.file))

                #try:
                file_label['text'] = str(self.file)

                ## Yield a list containing data
                ## avergaed over 'point_limit' number of
                ## chronoamperomegrams
                yield self.data_analysis()
            #except:
                    #print('\n\nChronoamperometryAnalysis.frames: Unable to yield data_analysis\n\n')


    def data_analysis(self):
        try:
            self.total_list = []
            self.index = 1

            #--- start the thread to analyze the data ---#
            #thread = threading.Thread(target = self.background_analyze()).start().join()          - NOPE
            self.analyze()

            ##########################################################
            ### Average the data from the merged data dictionaries ###
            ##########################################################
            sums = Counter()
            counters = Counter()
            for itemset in self.total_list:
                sums.update(itemset)
                counters.update(itemset.keys())

            try:
                averaged_data = {x: float(sums[x])/counters[x] for x in sums.keys()}
            except:
                averaged_data = None

            # return the average list

            return averaged_data

        except:
            print('\n\nChronoamperometryAnalysis.data_analysis: Error\n\n')
            t.sleep(5)


    def analyze(self):

        ###########################################################
        ### Iterate through each file that will used to create  ###
        ### a more accurate dataset of averaged data            ###
        ###########################################################
        while self.index <= self.point_limit:
            merged_dictionary = next(self.analysis_generator())
            self.total_list.append(merged_dictionary)
            t.sleep(0.01)


    #--- Generator function to return data to analyze ---#
    def analysis_generator(self):
        #--- Generator function that will yield data from all the potential steps
        #--- that will be averaged per file (titration point)
        while True:
            fig = figures['figure']

            print('\n\n\n POINT %s \n\n\n ' %str(self.index))

            ##############################
            ### Get data from the file ###
            ##############################
            short_time, short_currents  = self.retrieve_data('short')
            long_time, long_currents = self.retrieve_data('long')

            short_dictionary = {}
            count = 0
            for value in short_time:
                short_dictionary[value] = short_currents[count]
                count += 1

            long_dictionary = {}
            count = 0
            for value in long_time:
                long_dictionary[value] = long_currents[count]
                count += 1

            ###########################################
            ### Merge the two dictionaries into one ###
            ###########################################
            merged_dictionary = self.merge_two_dicts(short_dictionary, long_dictionary)

            t.sleep(0.001)

            self.index += 1

            yield merged_dictionary


    def retrieve_data(self, pulse):

        # variable used to tell retrive_data that the first
        # file has been found and that it should continue to
        # iterate through pulse_width/sample_rate number of files,
        # also known as 'variables'
        self.variable = False

        #--- get the file handle ---#
        if pulse == 'short':
            dictionary = self.short_dict
            variables = dictionary['variables']
            filehandle = 'Short_%s_#%d_#%d.DTA' % (handle_variable,self.file,self.index)
            aa = short_aa
            zz = short_zz

        elif pulse == 'long':
            dictionary = self.long_dict
            variables = dictionary['variables']
            filehandle = 'Long_%s_#%d_#%d.DTA' % (handle_variable,self.file,self.index)
            aa = long_aa
            zz = long_zz

        time = [0]*variables
        currents = [0]*variables

        myfile = mypath + filehandle


        ################################################################
        ### Create a loop in which the thread will continue to       ###
        ### search for the file for  'search_lim' amount of seconds  ###
        ################################################################
        try:
            mydata_bytes = os.path.getsize(myfile)    ### retrieves the size of the file in bytes
        except:
            print('\n\nChronoamperometryAnalysis.analyze: Could not find %s\n\n' % myfile)
            mydata_bytes = 1


        #---if the file meets the size requirement, analyze data---#
        if mydata_bytes > 1000:

            try:
                with open(myfile,'r',encoding='utf-8') as mydata:
                    val = 0
                    for line in mydata:
                        line = ' '.join(line.split())
                        line = line.strip()

                        if self.variable:
                            #print(line)
                            line = line.split(' ')

                            #--- extract the time ---#
                            seconds = line[1]

                            try:
                                #-- if its an exceptionally small number, it will
                                #-- be split with an 'E' exponent
                                seconds = seconds.split('E')
                                exponent = float(seconds[1])
                                seconds = float(seconds[0])
                                seconds = seconds * (10**exponent)

                            except:
                                seconds = seconds[0]
                            time[val] = seconds

                            #--- extract the current ---#
                            current = line[3]
                            current = current.split('E')
                            exponent = float(current[1])
                            current = float(current[0])
                            current = (current) * (10**(exponent))
                            #print('current: %s' % str(current))
                            currents[val] = current

                            #print('val: %s' % str(val))

                            #--- if this is the last file for this pulse, break ---#
                            if val == variables - 1:
                                self.variable = False
                                break

                            val += 1

                        #--- Find the first line and qery
                        elif line.startswith('1 '):
                            reduction_voltage = dictionary['reduction voltage']
                            reduction_voltage = self.volt_dict[reduction_voltage]
                            if reduction_voltage in line:
                                print('\n\n')
                                line = line.split(' ')
                                #print(line)
                                #t.sleep(1)

                                #--- extract the time ---#
                                seconds = line[1]
                                try:
                                    seconds = seconds.split('E')
                                    exponent = float(seconds[1])
                                    seconds = float(seconds[0])
                                    seconds = seconds * (10**exponent)

                                except:
                                    seconds = seconds[0]
                                time[val] = seconds

                                #--- extract the current ---#
                                current = line[3]
                                current = current.split('E')
                                exponent = float(current[1])
                                current = float(current[0])
                                current = (current) * (10**(exponent))
                                #print('current: %s' % str(current))
                                currents[val] = current

                                #print('start val: %s' % str(val))
                                #t.sleep(1)

                                val += 1

                                self.variable = True

                    time, currents = self._apply_adjustment(time, currents, aa, zz)

                    return time, currents

            except:
                print('Error in retrieve data')

        else:
            root.after(200, self.retrieve_data)

    def _apply_adjustment(self, time_list, current_list, aa, zz):

        time_list = [float(time) for time in time_list]

        zip_list = set(zip(time_list, current_list))

        # create a key,value dictionary with format {time: current}
        dict = {}
        for item in zip_list:
            time, current = item
            dict[time] = current

        adjusted_time = [time for time in time_list if aa <= time <= zz ]
        adjusted_currents = [dict[time] for time in adjusted_time]

        return adjusted_time, adjusted_currents

    def animate(self, framedata):

        #try:
        chronoamp_data = framedata
        time_data, current_data = zip(*sorted(chronoamp_data.items()))
        time_data = [abs(float(item)) for item in time_data]
        current_data = [abs(item) for item in current_data]

        # use a curve fitting function to extrpolate the
        # paramers of the exponential decay

        #####################################################################
        # popt: array = optimal parameters returned from least squares fit  #
        # pcov: 2D array = estimated covariance of popt                     #
        #####################################################################
        popt, pcov, C2 = self.set_fit(time_data, current_data)
        print(popt)

        # Get the time constant, lambda, with (1/k) from y = A * e^(-kt) + C
        fitted_lifetime = (1/popt[1])*1000                  # popt[1] = k
        self.fitted_lifetime_list.append(fitted_lifetime)

        # set the chronoamperogram
        self.raw_decay.set_data(time_data,current_data)     # raw curve


        # use the curve fitting function to approximate values
        # fot A,k, and C in y = A * e^(-kt) + C
        fitted_data = []
        for x in time_data:
            fit = self.biexponential_func(x, *popt, e = C2)     # use the curve fit parameters
            fitted_data.append(fit)                     # for each point in the chronoamperogram

        self.curve_fit.set_data(time_data,fitted_data)  # set the curve fit as an artist

        # set the half life plots
        file_list = range(1,self.file+1)
        self.fitted_lifetime.set_data(file_list,self.fitted_lifetime_list) # checking curve fit


        #export any relevant dat
        if SaveVar:
            export_data._export_data([self.file,fitted_lifetime])

        ### return artists to be animated
        return self.raw_decay, self.curve_fit, self.fitted_lifetime

        #except:
        #    print('\n\nError in animate\n\n')



    def merge_two_dicts(self, x, y):            # any keys that overlap will be overridden with the items from y
        z = x.copy()   # start with x's keys and values
        z.update(y)    # modifies z with y's keys and values & returns None
        return z




#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#



#################################################################
### Threaded animation class subclassing the animaiton module ###
#################################################################
class ThreadedAnimation(FuncAnimation):
    def __init__(self, fig, func, generator=None, interval=None):

        #-- this class will create parallel worker threads for separate animations,
        #-- improving the efficiency of the animation. Before, separate animations
        #-- would have to be run sequentially with multiple calls to FuncAnimation

        self.fig = fig
        self.func = func
        self.generator = generator
        self.interval = interval
        self.point_limit = point_limit

        #- Initialize FuncAnimation, which will subsequently initialize the
        #- animation module.
        FuncAnimation.__init__(self, self.fig, self.func, frames=self.generator, init_func = lambda: self.init(), interval=self.interval, blit=True)

    ##########################################################################
    ### Override the Animation._start method as to change the event source ###
    ### callback to a parallel thread as to increase performanace between  ###
    ### the UI and data visualization                                      ###
    ##########################################################################

    def init(self):
        #-- return an empty artist for the initial draw --#
        return plots['EmptyPlots'],

    def _start(self, *args):
        global event_source

        # Starts interactive animation. Adds the draw frame command to the GUI
        # handler, calls show to start the event loop.

        # First disconnect our draw event handler
        self._fig.canvas.mpl_disconnect(self._first_draw_id)
        self._first_draw_id = None  # So we can check on save

        # Now do any initial draw
        self._init_draw()


        #####################################################################################
        ### Thread class that will create a new thread instance as an event source that   ###
        ### spawns worker threads for data analysis. Multiple threads can carry out tasks ###
        ### from the queue at once, allowing for multiple worker threads to analyze and   ###
        ### animate separate artists simultaneously                                       ###
        #####################################################################################
        class _thread(threading.Thread):
            def __init__(self, callback=None):
                global ThreadQueue, PoisonPill

                threading.Thread.__init__(self)     # initiate the thread

                #-- set the poison pill event for Reset --#
                self.PoisonPill = Event()
                PoisonPill = self.PoisonPill             # global reference

                self.exp_low = exp_low
                self.exp_high = exp_high

                self.file = 1
                self.callback = callback
                self.q = Queue(maxsize=1)           # only allow a single worker to be placed on the queue at once
                ThreadQueue = self.q                      # global reference

                self.start()                        # initiate the run() method

            def run(self):

                ### continuously loop through workers, which will exit on their own ###
                while True:
                    if self.PoisonPill.isSet():
                        break

                    elif self.file > file_limit:
                        break

                    else:
                        try:

                            try:
                                if not ParameterPipe.empty():
                                    args = ParameterPipe.get()
                                    self.exp_low, self.exp_high = args
                                    print('\nRetrieved Parameters from the Pipe!\n')
                            except:
                                print('\n           Could not retrieve parameters from Queue\n\n')

                            print('\n_thread starting file %s\n' % str(self.file))
                            #########################################################
                            ### Place the next file to be analyzed into the queue ###
                            #########################################################
                            self.q.put(self.file)

                            ##########################################################
                            ### Could implement ability to animate multiple plots  ###
                            ### here using multiple threads instead of one         ###
                            ##########################################################
                            self.step_thread = Thread(target = self.callback).start()           # the callback is the _step method

                            #########################################################################
                            ### blocking call to wait until _step has finished analyzing the data ###
                            #########################################################################
                            self.q.join()   # blocks until the task_done() call is made at the end of _step

                            #-- Move onto the next file --#
                            self.file += 1

                        except:
                            print('\nError in _thread\n')
                            t.sleep(1)

                print('\nPoison Pill activated. Exiting Thread %s\n' % threading.current_thread())
                self.join()

        ############################################
        ### Inititiate the Threaded Event Source ###
        ############################################
        event_source = _thread(callback=self._step)

    ### Override of the animation.Animation() method to incorporate
    def _step(self):
        global ThreadQueue

        try:
            #--- retrieve the data from the generator function, frames() ---#
            framedata = next(self.frame_seq)

            #--- blit the data ---#
            self._draw_next_frame(framedata, self._blit)

            ############################################################
            ### Call task_done() to indicate _threads to continue    ###
            ###     - task_done() tells the queue.Queue object that  ###
            ###       all of the tasks within it are complete        ###
            ###     - this alleviates the lock created by q.join()   ###
            ############################################################
            ThreadQueue.task_done()

        except StopIteration:
            print('stop iteration')




##################################
### Real-Time Text File Export ###
##################################
class TextFileExport():

    ###############################
    ### Initialize the .txt file ###
    ###############################
    def __init__(self):
        self.TextFileHandle = FileHandle

        try:

            list = ['File','Lifetime (ms)']

            #--- Write the data into the .txt file ---#
            with open(FileHandle,'w+',encoding='utf-8', newline = '') as input:
                writer = csv.writer(input, delimiter = ' ')
                writer.writerow(list)

        except:
            print('\n\n','ERROR IN TEXT FILE EXPORT','\n\n')
            time.sleep(0.5)

    def _export_data(self, data):

        #--- Write the data into the .txt file ---#
        with open(FileHandle,'a',encoding='utf-8', newline = '') as input:
            writer = csv.writer(input, delimiter = ' ')
            writer.writerow(data)
        with open(FileHandle,'r',encoding='utf-8', newline = '') as filecontents:
            filedata =  filecontents.read()
        filedata = filedata.replace('[','')
        filedata = filedata.replace('"','')
        filedata = filedata.replace(']','')
        filedata = filedata.replace(',','')
        filedata = filedata.replace('\'','')
        with open(FileHandle,'w',encoding='utf-8', newline = '') as output:
            output.write(filedata)




#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

                    ############################################
                    ### Initialize GUI to start the program  ###
                    ############################################

if __name__ == '__main__':

    root = RealTimeAnalysis()

    #-- Button Styling --#
    style = ttk.Style()
    style.configure('On.TButton', foreground = 'blue', font = LARGE_FONT, relief = 'raised', border = 100)
    style.configure('Off.TButton', foreground = 'black', font = MEDIUM_FONT, relief = 'sunken', border = 5)



    while True:
        #--- initiate the mainloop ---#
        try:
            root.mainloop()
        #--- escape scrolling error ---#
        except UnicodeDecodeError:
            pass


                    #*########################################*#
                    #*############ End of Program ############*#
                    #*########################################*#
