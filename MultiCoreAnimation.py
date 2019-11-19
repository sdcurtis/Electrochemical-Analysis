## Incorporating Multiprocessing into ElectrochemicalAnimation ##


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
import scipy
from scipy import *
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
import multiprocessing
from multiprocessing import Process

    ##########################################################################
    ##########################################################################
    ###   ANIMATION FUNCTION TO HANDLE ALL DATA ANALYSIS AND VISUALIZATION ###
    ##########################################################################
    ##########################################################################

fig1 = plt.figure(figsize=(9,6),constrained_layout=True) # (width, height)
ax1 = fig1.add_subplot(111)

fig2 = plt.figure(figsize=(9,6),constrained_layout=True) # (width, height)
ax2 = fig2.add_subplot(111)

figs = [fig1,fig2]
ax = [ax1,ax2]

class ElectrochemicalAnimation():
    def __init__(self, generator = None, func = None, resize_interval = None, fargs = None):


        ##############################
        ## Set the generator object ##
        ##############################
        if generator is not None:
            self.generator = generator
        else:
            self.generator = self._raw_generator

        ################################
        ## Set the animation function ##
        ################################
        if func is not None:
            self._func = func
        else:
            self._func = self._animate

        # Disables blitting for backends that don't support it.  This
        # allows users to request it if available, but still have a
        # fallback that works if it is not.
        self._blit = fig.canvas.supports_blit


        # Instead of starting the event source now, we connect to the figure's
        # draw_event, so that we only start once the figure has been drawn.
        self._first_draw_id = fig.canvas.mpl_connect('draw_event', self._start)

        # Connect to the figure's close_event so that we don't continue to
        # fire events and try to draw to a deleted figure.
        self._close_id = self._fig.canvas.mpl_connect('close_event', self._stop)

        self._setup_blit()


    def _start(self, *args):


        # Starts interactive animation. Adds the draw frame command to the GUI
        # andler, calls show to start the event loop.

        # First disconnect our draw event handler
        self._fig.canvas.mpl_disconnect(self._first_draw_id)
        self._first_draw_id = None  # So we can check on save

        # Now do any initial draw
        self._init_draw()

        ### Create a thread to analyze obtain the file from a Queue
        ### and analyze the data.

        class _threaded_animation(multiprocessing.Process):

            def __init__(self, Queue):
                #global PoisonPill
                print('1')

                multiprocessing.Process.__init__(self)     # initiate the thread

                self.q = Queue

                #-- set the poison pill event for Reset --#
                self.PoisonPill = Event()
                PoisonPill = self.PoisonPill             # global reference

                self.file = 1

                root.after(10,self.start)                       # initiate the run() method

            def run(self):
                print("2")
                while True:
                    try:
                        task = self.q.get(block=False)
                        print('3')
                    except:
                        break
                    else:
                        if not PoisonPill:
                            print('4')
                            print(task)
                            task()
                            #root.after(Interval,task)

                if not analysis_complete:
                    if not PoisonPill:
                        print('running again')
                        self.run()


        threaded_animation = _threaded_animation(Queue = q)

        self._step()


    def _stop(self, *args):
        # On stop we disconnect all of our events.
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._fig.canvas.mpl_disconnect(self._close_id)

    def _setup_blit(self):
        # Setting up the blit requires: a cache of the background for the
        # axes
        self._blit_cache = dict()
        self._drawn_artists = []
        self._resize_id = self._fig.canvas.mpl_connect('resize_event',
                                                       self._handle_resize)
        self._post_draw(True)

    def _blit_clear(self, artists, bg_cache):
        # Get a list of the axes that need clearing from the artists that
        # have been drawn. Grab the appropriate saved background from the
        # cache and restore.
        axes = {a.axes for a in artists}
        for a in axes:
            if a in bg_cache:
                a.figure.canvas.restore_region(bg_cache[a])


    #######################################################################
    ### Initialize the drawing by returning a sequence of blank artists ###
    #######################################################################
    def _init_draw(self):

        self._drawn_artists = EmptyPlots

        for a in self._drawn_artists:
            a.set_animated(self._blit)

    def _redraw_figures(self):

        ############################################
        ### Resize raw and normalized data plots ###
        ############################################

        if self.analysis_boolean:
            figures[self.num]['data analysis'].set_xlim(0,self.resize_limit+0.1)

        if self.potential_boolean:
            if self.forward_boolean:
                figures[self.num]['forward plot'].set_xlim(0,self.resize_limit+0.1)
            if self.reverse_boolean:
                figures[self.num]['reverse plot'].set_xlim(0,self.resize_limit+0.1)

        if self.probe1_boolean:
            figures[self.num]['volt1 plot'].set_xlim(0,self.resize_limit+0.1)
        if self.probe2_boolean:
            figures[self.num]['volt2 plot'].set_xlim(0,self.resize_limit+0.1)


        #####################################################
        ### Set up the new canvas with an idle draw event ###
        #####################################################
        self._post_draw(True)


    def _handle_resize(self, *args):
        # On resize, we need to disable the resize event handling so we don't
        # get too many events. Also stop the animation events, so that
        # we're paused. Reset the cache and re-init. Set up an event handler
        # to catch once the draw has actually taken place.

        #################################################
        ### Stop the event source and clear the cache ###
        #################################################
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._blit_cache.clear()
        self._init_draw()
        self._resize_id = self._fig.canvas.mpl_connect('draw_event',
                                                       self._end_redraw)


    def _end_redraw(self, evt):
        # Now that the redraw has happened, do the post draw flushing and
        # blit handling. Then re-enable all of the original events.
        self._post_draw(True)
        self._fig.canvas.mpl_disconnect(self._resize_id)
        self._resize_id = self._fig.canvas.mpl_connect('resize_event',
                                                       self._handle_resize)

    def _draw_next_frame(self, framedata, fargs = None):
        # Breaks down the drawing of the next frame into steps of pre- and
        # post- draw, as well as the drawing of the frame itself.
        print('draw next frame')
        self._pre_draw(framedata)
        self._draw_frame(framedata, fargs)
        self._post_draw(False)


    def _pre_draw(self, framedata):
        # Perform any cleaning or whatnot before the drawing of the frame.
        # This default implementation allows blit to clear the frame.
        self._blit_clear(self._drawn_artists, self._blit_cache)

    ###########################################################################
    ### Retrieve the data from _animation and blit the data onto the canvas ###
    ###########################################################################
    def _draw_frame(self, framedata, fargs):
        print('draw frame')

        self._drawn_artists = self._func(framedata, *self._args)

        if self._drawn_artists is None:
            raise RuntimeError('The animation function must return a '
                               'sequence of Artist objects.')
        self._drawn_artists = sorted(self._drawn_artists,
                                     key=lambda x: x.get_zorder())

        for a in self._drawn_artists:
            a.set_animated(self._blit)


    def _post_draw(self, redraw):
        print('post draw')
        # After the frame is rendered, this handles the actual flushing of
        # the draw, which can be a direct draw_idle() or make use of the
        # blitting.

        if redraw:

            # Data plots #
            self._fig.canvas.draw()


        elif self._drawn_artists:

            self._blit_draw(self._drawn_artists, self._blit_cache)


    # The rest of the code in this class is to facilitate easy blitting
    def _blit_draw(self, artists, bg_cache):
        print('Blit Draw')
        # Handles blitted drawing, which renders only the artists given instead
        # of the entire figure.
        updated_ax = []
        for a in artists:
            # If we haven't cached the background for this axes object, do
            # so now. This might not always be reliable, but it's an attempt
            # to automate the process.
            if a.axes not in bg_cache:
                bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox)
            a.axes.draw_artist(a)
            updated_ax.append(a.axes)

        # After rendering all the needed artists, blit each axes individually.
        for ax in set(updated_ax):
            print('blitting...')
            ax.figure.canvas.blit(ax.bbox)

        print('next...')
        self._next_iteration()


    ## callback that is called every 'interval' ms ##
    def _step(self):
        global file_list, analysis_complete

        print('step')
        if self.file not in self.file_list:
            self.file_list.append(self.file)

        filename, filename2 = _retrieve_file(self.file, self.electrode)

        myfile = mypath + filename                    ### path of raw data .csv file
        myfile2 = mypath + filename2                   ### path of raw data .csv file

        try:
            mydata_bytes = os.path.getsize(myfile)    ### retrieves the size of the file in bytes

        except:
            mydata_bytes = 1

        try:
            mydata_bytes2 = os.path.getsize(myfile2)    ### retrieves the size of the file in bytes

        except:
            mydata_bytes2 = 1

        #################################################################
        #### If the file meets the size requirement, analyze the data ###
        #################################################################
        if mydata_bytes > 1000:
            #self.FileLabel['text'] = 'Found %s' % filename
            q.put(lambda: self._run_analysis(myfile))

        elif mydata_bytes2 > 1000:
            q.put(lambda: self._run_analysis(myfile2))

        else:
            if not PoisonPill:
                root.after(100,self._step)

    def _check_queue():

        while True:
            try:
                task = q.get(block=False)
            except:
                break
            else:
                if not PoisonPill:
                    root.after(1,self.task)

        if not analysis_complete:
            if not PoisonPill:
                root.after(5, self._check_queue)

    def _run_analysis(self,myfile):
        global post_analysis

        print('_run_analysis %d' % self.electrode)
        #######################################################
        ### Perform the next iteration of the data analysis ###
        #######################################################
        try:
            framedata = self.generator(myfile)
            self._draw_next_frame(framedata)
            print('5')
        except StopIteration:
            return False

    def _next_iteration(self):
        print('_next_iteration')
        ##########################################################################
        ### if the resize limit has been reached, resize and redraw the figure ###
        ##########################################################################
        if self.file == self.resize_limit:

            # Dont redraw if this is the already the last file #
            if self.resize_limit < numFiles:

                self.resize_limit = self.resize_limit + self.resize_interval

                ### If the resize limit is above the number of files (e.g.
                ### going out of bounds for the last resize event) then
                ### readjust the final interval to the number of files
                if self.resize_limit >= numFiles:
                    self.resize_limit = numFiles

                ############################################################
                ### 'if' statement used to make sure the plots dont get  ###
                ### erased when there are no more files to be visualized ###
                ############################################################
                try:
                    self._redraw_figures()
                except:
                    print('\nCould not redraw figure\n')

        track.tracking(self.file)

        #########################################################################
        ### If the function has analyzed the final final, remove the callback ###
        #########################################################################
        if self.file == numFiles:
            print('\n%sFILE %s.\n%sElectrode %d\n%sData Analysis Complete\n' % (self.spacer,str(self.file),self.spacer,self.electrode,self.spacer))

            #post_analysis._analysis_finished()

        else:
            self.file += 1
            self.index += 1
            print('%smoving onto file %s\n' % (self.spacer,str(self.file)))
            self._step()


    def _raw_generator(self, myfile):

      data = np.linspace(0,100)
    ######################################################
    ### Retrieve the processed data from the generator ###
    ### and animate ('blit') it onto the artists       ###
    ######################################################
    def _animate(self, framedata, *args):

        if key > 0:

            #####################################################
            ### Retrieve the data from the generator function ###
            #####################################################
            segment_data, adjusted_segment_data, baseline_data, vertex_data = framedata

            ################################################################
            ### Acquire the artists for this electrode at this frequency ###
            ### and get the data that will be visualized                 ###
            ################################################################
            plots = plot_list[self.num]

            if self.forward_boolean:
                ########################
                ### Forwards Segment ###
                ########################
                #-- raw data --#
                forward_data = segment_data['forward']
                forward_potentials = forward_data[0]
                forward_currents = forward_data[1]

                #-- data adjusted to user chosen voltage range --#
                adjusted_forward_data = adjusted_segment_data['forward']
                adjusted_forward_potentials = adjusted_forward_data[0]
                adjusted_forward_currents = adjusted_forward_data[1]

                #-- set the x and y data of the artists to be animated --#
                plots['raw forward'].set_data(forward_potentials,forward_currents)
                plots['adjusted forward'].set_data(adjusted_forward_potentials,adjusted_forward_currents)

                #-- linear baseline data --#
                if self.analysis_boolean:
                    forward_baseline = baseline_data['forward']
                    forward_baseline_potentials = forward_baseline[0]
                    forward_baseline_currents = forward_baseline[1]

                    plots['forward baseline'].set_data(forward_baseline_potentials,forward_baseline_currents)
                    plots['forward poly'].set_xy(vertex_data['forward'])


                #######################
                ### Peak Height/AUC ###
                #######################
                if self.analysis_boolean:
                    plots['forward data'].set_data(self.file_list,data_list[self.num]['forward'][:len(self.file_list)])   # Forwards


                #################
                ### Voltage 1 ###
                #################
                if self.probe1_boolean:
                    plots['volt1 forward'].set_data(self.file_list,voltage1_data[self.num]['forward'][:len(self.file_list)])

                #################
                ### Voltage 2 ###
                #################
                if self.probe2_boolean:
                    plots['volt2 forward'].set_data(self.file_list,voltage2_data[self.num]['forward'][:len(self.file_list)])

                #######################
                ### Peak Potentials ###
                #######################
                if self.potential_boolean:
                    plots['peak forward'].set_data(self.file_list,peak_data_list[self.num]['forward'][:len(self.file_list)])   # Forwards

            if self.reverse_boolean:
                #######################
                ### Reverse Segment ###
                #######################
                #-- raw data --#
                reverse_data = segment_data['reverse']
                reverse_potentials = reverse_data[0]
                reverse_currents = reverse_data[1]

                #-- data adjusted to user chosen voltage range --#
                adjusted_reverse_data = adjusted_segment_data['reverse']
                adjusted_reverse_potentials = adjusted_reverse_data[0]
                adjusted_reverse_currents = adjusted_reverse_data[1]


                #-- set the x and y data of the artists to be animated --#
                plots['raw reverse'].set_data(reverse_potentials,reverse_currents)
                plots['adjusted reverse'].set_data(adjusted_reverse_potentials,adjusted_reverse_currents)

                if self.analysis_boolean:

                    #-- linear baseline data --#
                    reverse_baseline = baseline_data['reverse']
                    reverse_baseline_potentials = reverse_baseline[0]
                    reverse_baseline_currents = reverse_baseline[1]

                    plots['reverse baseline'].set_data(reverse_baseline_potentials,reverse_baseline_currents)
                    plots['reverse poly'].set_xy(vertex_data['reverse'])

                #######################
                ### Peak Height/AUC ###
                #######################
                if self.analysis_boolean:
                    plots['reverse data'].set_data(self.file_list,data_list[self.num]['reverse'][:len(self.file_list)])   # Reverse

                #################
                ### Voltage 1 ###
                #################
                if self.probe1_boolean:
                    plots['volt1 reverse'].set_data(self.file_list,voltage1_data[self.num]['reverse'][:len(self.file_list)])

                #################
                ### Voltage 2 ###
                #################
                if self.probe2_boolean:
                    plots['volt2 reverse'].set_data(self.file_list,voltage2_data[self.num]['reverse'][:len(self.file_list)])

                #######################
                ### Peak Potentials ###
                #######################
                if self.potential_boolean:
                    plots['peak reverse'].set_data(self.file_list,peak_data_list[self.num]['reverse'][:len(self.file_list)])   # Forwards


            print('\n%s %d %s_animate\n' % (self.spacer,self.electrode,self.spacer))

            vis_plots = [value for (key,value) in plots.items()]

            return vis_plots


        else:
            file = 1
            EmptyPlots = framedata
            time.sleep(0.1)
            print('\n Yielding Empty Plots in Animation \n')
            return EmptyPlots
