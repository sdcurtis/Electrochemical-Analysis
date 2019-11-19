import SACMES_SWV as SWV

#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

                                    ########################
                                    ### Import Libraries ###
                                    ########################


#---Clear mac terminal memory---#
import os
import matplotlib
matplotlib.use('TkAgg')
os.system("clear && printf '\e[3J'")

#---Import Modules---#
import sys
import time
import datetime
try:
    import Tkinter as tk
    from Tkinter.ttk import *
    from Tkinter import *
    from Tknter import filedialog, Menu

except ImportError: # Python 3
    import tkinter as tk
    from tkinter.ttk import *
    from tkinter import *
    from tkinter import filedialog, Menu
    from tkinter.messagebox import showinfo


from matplotlib import style
import scipy.integrate as integrate
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import csv
from pylab import *
from numpy import *
from scipy.interpolate import *
from scipy.integrate import simps
from scipy.signal import *
from itertools import *
from math import log10, floor
from decimal import Decimal
from operator import truediv
import threading
from threading import Thread
from queue import Queue
style.use('ggplot')

#---Filter out error warnings---#
import warnings
warnings.simplefilter('ignore', np.RankWarning)         #numpy polyfit_deg warning
warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd") #RuntimeWarning


#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

#-- file handle variable --#
handle_variable = ''    # default handle variable is nothing
e_var = 'single'        # default input file is 'Multichannel', or a single file containing all electrodes
PHE_method = 'Abs'      # default PHE Extraction is difference between absolute max/min

#------------------------------------------------------------#

InputFrequencies = [30,80,240]  # frequencies initially displayed in Frequency Listbox
electrodes = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

#---------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------#

                                    ########################
                                    ### Global Variables ###
                                    ########################

########################################
### Polynomial Regression Parameters ###
########################################
sg_window = 5           ### Savitzky-Golay window (in mV range), must be odd number (increase signal:noise)
sg_degree = 1           ### Savitzky-Golay polynomial degree
polyfit_deg = 15        ### degree of polynomial fit

cutoff_frequency = 50          ### frequency that separates 'low' and 'high'
                               ### frequencies for regression analysis and
                               ### smoothing manipulation

#############################
### Checkpoint Parameters ###
#############################
key = 0                 ### SkeletonKey
search_lim = 15         ### Search limit (sec)
PoisonPill = False      ### Stop Animation variable
FoundFilePath = False   ### If the user-inputted file is found
ExistVar = False        ### If Checkpoints are not met ExistVar = True
AlreadyInitiated = False    ### indicates if the user has already initiated analysis
HighAlreadyReset = False    ### If data for high frequencies has been reset
LowAlreadyReset = False      ### If data for low frequencies has been reset
analysis_complete = False    ### If analysis has completed, begin PostAnalysis

##################################
### Data Extraction Parameters ###
##################################
delimiter = 1               ### default delimiter is a space; 2 = tab
extension = 1
current_column = 4           ### column index for list_val.
current_column_index = 3
                              # list_val = column_index + 3
                              # defauly column is the second (so index = 1)
voltage_column = 1
voltage_column_index = 0

spacing_index = 3

######################################################
### Low frequency baseline manipulation Parameters ###
######################################################
LowFrequencyOffset = 0         ### Vertical offset of normalized data for
                               ### user specified 'Low Frequency'
LowFrequencySlope = 0          ### Slope manipulation of norm data for user
                               ### specified 'Low Frequency'


###############
### Styling ###
###############
HUGE_FONT = ('Verdana', 18)
LARGE_FONT = ('Verdana', 11)
MEDIUM_FONT = ('Verdnana', 10)
SMALL_FONT = ('Verdana', 8)


                        ########################
                        ### Global Functions ###
                        ########################


print('woo!')


if __name__ == '__main__':

    root = tk.Tk()
    app = SWV.MainWindow(root)

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
