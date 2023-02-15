#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timoth?Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtWidgets
from numpy import log10, where, sign, arange, zeros,floor, float64
# from friture.timeplot import TimePlot
from friture.timeplot_fft_time_plot import TimePlot
from friture.audiobackend import SAMPLING_RATE


import logging
from friture.audioproc import audioproc  # audio processing class
from friture.spectrum_settings import (Spectrum_Settings_Dialog,  # settings dialog
                                       DEFAULT_FFT_SIZE,
                                       DEFAULT_FREQ_SCALE,
                                       DEFAULT_MAXFREQ,
                                       DEFAULT_MINFREQ,
                                       DEFAULT_SPEC_MIN,
                                       DEFAULT_SPEC_MAX,
                                       DEFAULT_WEIGHTING,
                                       DEFAULT_RESPONSE_TIME,
                                       DEFAULT_SHOW_FREQ_LABELS)

SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
DEFAULT_TIMERANGE = 2 * SMOOTH_DISPLAY_TIMER_PERIOD_MS
DEFAULT_FREQUENCY1 = 6200
DEFAULT_FREQUENCY2 = 6000

DEFAULT_MIN=-200
DEFAULT_MAX=30



SMOOTH_DISPLAY_TIMER_PERIOD_MS = 25
DEFAULT_TIMERANGE = 2 * SMOOTH_DISPLAY_TIMER_PERIOD_MS


class Scope_Widget1(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self.audiobuffer = None

        self.setObjectName("Scope_Widget")
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.PlotZoneUp = TimePlot(self)
        self.PlotZoneUp.setObjectName("PlotZoneUp")

        self.PlotZoneUp.setverticaltitle("FFT amplitude (dB)")
        self.PlotZoneUp.sethorizontaltitle("Time (s)")


        self.gridLayout.addWidget(self.PlotZoneUp, 0, 0, 1, 1)

        self.settings_dialog = Scope_Settings_Dialog(self)


        # initialize the class instance that will do the fft
        self.proc = audioproc()

        self.fft_size = 2 ** DEFAULT_FFT_SIZE * 32 #8192


        # timerange =  300  # Here in this code is actually the fft points of the fft buffer

        # self.set_timerange(timerange)
        self.proc.set_fftsize(self.fft_size)

        self.freq = self.proc.get_freq_scale()

        self.buffersize=800 #how many fft points to save
        self.buff1=zeros(self.buffersize)
        self.buff2=zeros(self.buffersize)
        self.buff0=zeros(self.buffersize)
        self.buff3=zeros(self.buffersize)



        self.set_frequency1(DEFAULT_FREQUENCY1)
        self.set_frequency2(DEFAULT_FREQUENCY2)

        self.RANGE_MIN=DEFAULT_MIN # self.RANGE_MIN will set the minimum value of the y axis in the GUI
        self.RANGE_MAX=DEFAULT_MAX # unit is volt here
        # self._scope_data.vertical_axis.setRange(1000*self.RANGE_MIN, 1000*self.RANGE_MAX)# Make the unit to be mV
        # self._scope_data.vertical_axis.setRange( self.RANGE_MIN, self.RANGE_MAX)# This is simply the range of the label in y axis, has no real relation to the y data.
       
        self.old_index = 0
        self.overlap = 3. / 4.
        self.dual_channels = True

        timerange =  int(self.fft_size*(1-self.overlap)*self.buffersize/float(SAMPLING_RATE))

        self.set_timerange(timerange)



    # method
    def set_buffer(self, buffer):
        self.audiobuffer = buffer
        self.old_index = self.audiobuffer.ringbuffer.offset

    def handle_new_data(self, floatdata):

        #####################
        # we need to maintain an index of where we are in the buffer
        index = self.audiobuffer.ringbuffer.offset

        available = index - self.old_index

        if available < 0:
            # ringbuffer must have grown or something...
            available = 0
            self.old_index = index

        # if we have enough data to add a frequency column in the time-frequency plane, compute it
        needed = self.fft_size * (1. - self.overlap)
        realizable = int(floor(available / needed)) #floor is "quzheng" in Chinese

        twoChannels = True
        if realizable > 0:
            sp1n = zeros((len(self.freq), realizable), dtype=float64)
            sp2n = zeros((len(self.freq), realizable), dtype=float64)

            for i in range(realizable):
                floatdata = self.audiobuffer.data_indexed(self.old_index, self.fft_size)

                # first channel
                # FFT transform
                sp1n[:, i] = self.proc.analyzelive(floatdata[0, :])

                if self.dual_channels and floatdata.shape[0] > 1:
                    # second channel for comparison
                    sp2n[:, i] = self.proc.analyzelive(floatdata[1, :])

                self.old_index += int(needed)
            # twoChannels = False
            # if floatdata.shape[0] > 1:
            #     twoChannels = True

            # if twoChannels and len(self._scope_data.plot_items) == 1:
            #     self._scope_data.add_plot_item(self._curve_2)
            # elif not twoChannels and len(self._scope_data.plot_items) == 2:
            #     self._scope_data.remove_plot_item(self._curve_2)


        ###########################################################################
            self.freq1=self.frequency1 # frequency I am interested in to extract fft amp ####
            self.freq2=self.frequency2                                                   ####
        ###########################################################################
            self.freq_idx1=(abs(self.freq-self.freq1)).argmin()
            self.freq_idx2=(abs(self.freq-self.freq2)).argmin()
            #check self.freq[self.freq_idx1] , see if it is close to 1000

            data=sp1n[self.freq_idx1]
            data=self.log_spectrogram(data)
            

            self.buff0=self.buff1
            self.buff1[-1]=data
            self.buff1[:-1]=self.buff0[1:]
            # for i in range(len(self.buff1)-1):
            #     self.buff1[i]=self.buff0[i+1]

            b=self.buff1
            a=arange(self.buffersize)

            a=(self.fft_size*(1-self.overlap)/float(SAMPLING_RATE))*a
            
            b_min=min(b)
            b_max=max(b)
            
            # #Kingson: trying to plot in autoscale in y axis. 
            # The y axis ticker is set in above in this function: self._scope_data.vertical_axis.setRange
            self.RANGE_MIN=b_min-0.1*(b_max-b_min)
            self.RANGE_MAX=b_max+0.1*(b_max-b_min)
            self.set_yrange(self.RANGE_MIN, self.RANGE_MAX)# Make the unit to be mV



            # scaled_a=a/self.buffersize

            # range_min=self.RANGE_MIN #the minimum value that the target signal can reach at target frequency
            # range_max=self.RANGE_MAX

            # range_middle=(range_min+range_max)/2
            # range_length=range_max-range_min

            # b=(b-range_middle)/(range_length/2)  #turn b into the range (-1, 1)

            # scaled_b=1-(b+1)/2.  #turn scaled_b into the range (1,0)



            # self._curve.setData(scaled_a, scaled_b)
#####################################################
            if twoChannels:
                data2=sp2n[self.freq_idx2]
                data2=self.log_spectrogram(data2)

                self.buff2=self.buff3
                self.buff3[-1]=data2
                # for i in range(len(self.buff3)-1):
                #     self.buff3[i]=self.buff2[i+1]
                self.buff3[:-1]=self.buff2[1:]

                b1=self.buff3
                # a=arange(self.buffersize)

                # scaled_a=a/self.buffersize

                # b1=(b1-range_middle)/(range_length/2)  #turn b into the range (-1, 1)
                # scaled_b1=1-(b1+1)/2.

                # self._curve_2.setData(scaled_a, scaled_b)
                
                # self.PlotZoneUp.setdataTwoChannels(scaled_a, b, b1)
                self.PlotZoneUp.setdataTwoChannels(a, b, b1)

            # filtered = signal.sosfiltfilt(sos, scaled_b)
            # self._curve_2.setData(scaled_a, filtered)


        """
        datarange=240, datarange=width, width is number of samples.
                time = self.timerange * 1e-3  #self.timerange is the time set by user in ms.
                width = int(time * SAMPLING_RATE)

        len(self.y)=240
        SAMPLING_RATE=48000

        """

    def set_timerange(self, timerange):
        self.timerange = timerange
        self.PlotZoneUp.settimerange(0,timerange)
        # self._scope_data.horizontal_axis.setRange(0, self.timerange)
        # self._scope_data.horizontal_axis.setRange(-self.timerange/2., self.timerange/2.)
        # self._scope_data.vertical_axis.setRange(0., 1.)


    def set_yrange(self, ymin, ymax):
        # change the y axis tickers in the GUI
        self.RANGE_MIN=ymin # self.RANGE_MIN will set the minimum value of the y axis in the GUI
        self.RANGE_MAX=ymax # unit is volt here, 1.2 here is to make sure the data peaks are not cropped
        # self._scope_data.vertical_axis.setRange(self.RANGE_MIN, self.RANGE_MAX)# Make the unit in the plot to be mV
        self.PlotZoneUp.setverticalrange(self.RANGE_MIN,self.RANGE_MAX)

    def setmin(self, value):
        self.RANGE_MIN = value # dB
        self.set_yrange(self.RANGE_MIN, self.RANGE_MAX)

    def setmax(self, value):
        self.RANGE_MAX = value  # dB
        self.set_yrange(self.RANGE_MIN, self.RANGE_MAX)

    def set_frequency1(self, frequency):
        self.frequency1 = frequency
        self.PlotZoneUp.curve.setTitle("Ch1")
        self.PlotZoneUp.update()
        # self._scope_data.horizontal_axis.setRange(0, self.timerange)

    def set_frequency2(self, frequency):
        self.frequency2 = frequency
        self.PlotZoneUp.curve2.setTitle("Ch2")
        self.PlotZoneUp.update()
        # self._curve_2.name = "Ch2 at "+str(self.frequency2) +" Hz"
        # self._scope_data.horizontal_axis.setRange(0, self.timerange)
       
        # time = self.timerange * 1e-3
        # width = int(time * SAMPLING_RATE)
        # # basic trigger capability on leading edge
        # floatdata = self.audiobuffer.data(2 * width)

        # twoChannels = False
        # if floatdata.shape[0] > 1:
        #     twoChannels = True

        # # trigger on the first channel only
        # triggerdata = floatdata[0, :]
        # # trigger on half of the waveform
        # trig_search_start = width // 2
        # trig_search_stop = -width // 2
        # triggerdata = triggerdata[trig_search_start: trig_search_stop]

        # trigger_level = floatdata.max() * 2. / 3.
        # trigger_pos = where((triggerdata[:-1] < trigger_level) * (triggerdata[1:] >= trigger_level))[0]

        # if len(trigger_pos) == 0:
        #     return

        # if len(trigger_pos) > 0:
        #     shift = trigger_pos[0]
        # else:
        #     shift = 0
        # shift += trig_search_start
        # datarange = width
        # floatdata = floatdata[:, shift - datarange // 2: shift + datarange // 2]

        # self.y = floatdata[0, :]
        # if twoChannels:
        #     self.y2 = floatdata[1, :]
        # else:
        #     self.y2 = None

        # dBscope = False
        # if dBscope:
        #     dBmin = -50.
        #     self.y = sign(self.y) * (20 * log10(abs(self.y))).clip(dBmin, 0.) / (-dBmin) + sign(self.y) * 1.
        #     if twoChannels:
        #         self.y2 = sign(self.y2) * (20 * log10(abs(self.y2))).clip(dBmin, 0.) / (-dBmin) + sign(self.y2) * 1.
        #     else:
        #         self.y2 = None

        # self.time = (arange(len(self.y)) - datarange // 2) / float(SAMPLING_RATE)

        # if self.y2 is not None:
        #     self.PlotZoneUp.setdataTwoChannels(self.time*1e3, self.y, self.y2)
        # else:
        #     self.PlotZoneUp.setdata(self.time*1e3, self.y)

    # method
    def canvasUpdate(self):
        return

    def pause(self):
        self.PlotZoneUp.pause()

    def restart(self):
        self.PlotZoneUp.restart()

    # # slot
    # def set_timerange(self, timerange):
    #     self.timerange = timerange

    # slot
    def settings_called(self, checked):
        self.settings_dialog.show()

    # method
    def saveState(self, settings):
        self.settings_dialog.saveState(settings)

    # method
    def restoreState(self, settings):
        self.settings_dialog.restoreState(settings)

    def log_spectrogram(self, sp):
        # Note: implementing the log10 of the array in Cython did not bring
        # any speedup.
        # Idea: Instead of computing the log of the data, I could pre-compute
        # a list of values associated with the colormap, and then do a search...
        epsilon = 1e-30
        return 10. * log10(sp + epsilon)

class Scope_Settings_Dialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        # self.setWindowTitle("Scope settings")

        # self.formLayout = QtWidgets.QFormLayout(self)

        # self.doubleSpinBox_timerange = QtWidgets.QDoubleSpinBox(self)
        # self.doubleSpinBox_timerange.setDecimals(1)
        # self.doubleSpinBox_timerange.setMinimum(0.1)
        # self.doubleSpinBox_timerange.setMaximum(1000.0)
        # self.doubleSpinBox_timerange.setProperty("value", DEFAULT_TIMERANGE)
        # self.doubleSpinBox_timerange.setObjectName("doubleSpinBox_timerange")
        # self.doubleSpinBox_timerange.setSuffix(" ms")

        # self.formLayout.addRow("Time range:", self.doubleSpinBox_timerange)

        # self.setLayout(self.formLayout)

        # self.doubleSpinBox_timerange.valueChanged.connect(self.parent().set_timerange)
        self.setWindowTitle("FFT_Points Scope settings")

        self.formLayout = QtWidgets.QFormLayout(self)

        self.doubleSpinBox_frequency1 = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_frequency1.setDecimals(0)
        self.doubleSpinBox_frequency1.setMinimum(20)
        self.doubleSpinBox_frequency1.setMaximum(20000)
        self.doubleSpinBox_frequency1.setProperty("value", DEFAULT_FREQUENCY1)
        self.doubleSpinBox_frequency1.setObjectName("doubleSpinBox_frequency1")
        self.doubleSpinBox_frequency1.setSuffix(" Hz")

        self.doubleSpinBox_frequency2 = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_frequency2.setDecimals(0)
        self.doubleSpinBox_frequency2.setMinimum(20)
        self.doubleSpinBox_frequency2.setMaximum(20000)
        self.doubleSpinBox_frequency2.setProperty("value", DEFAULT_FREQUENCY2)
        self.doubleSpinBox_frequency2.setObjectName("doubleSpinBox_frequency2")
        self.doubleSpinBox_frequency2.setSuffix(" Hz")

        self.doubleSpinBox_min = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_min.setDecimals(1)
        self.doubleSpinBox_min.setMinimum(-220)
        self.doubleSpinBox_min.setMaximum(10)
        self.doubleSpinBox_min.setProperty("value", DEFAULT_MIN)
        self.doubleSpinBox_min.setObjectName("doubleSpinBox_min")
        self.doubleSpinBox_min.setSuffix(" dB")

        self.doubleSpinBox_max = QtWidgets.QDoubleSpinBox(self)
        self.doubleSpinBox_max.setDecimals(1)
        self.doubleSpinBox_max.setMinimum(-220)
        self.doubleSpinBox_max.setMaximum(10)
        self.doubleSpinBox_max.setProperty("value", DEFAULT_MAX)
        self.doubleSpinBox_max.setObjectName("doubleSpinBox_max")
        self.doubleSpinBox_max.setSuffix(" dB")

        # self.formLayout.addRow("Time range:", self.doubleSpinBox_timerange)
        self.formLayout.addRow("Target frequency at Ch1:", self.doubleSpinBox_frequency1)
        self.formLayout.addRow("Target frequency at Ch2:", self.doubleSpinBox_frequency2)
        self.formLayout.addRow("Min level: ", self.doubleSpinBox_min)
        self.formLayout.addRow("Max level: ", self.doubleSpinBox_max)

        self.setLayout(self.formLayout)

        # self.doubleSpinBox_timerange.valueChanged.connect(self.parent().set_timerange)
        self.doubleSpinBox_frequency1.valueChanged.connect(self.parent().set_frequency1)
        self.doubleSpinBox_frequency2.valueChanged.connect(self.parent().set_frequency2)

        self.doubleSpinBox_min.valueChanged.connect(self.parent().setmin)
        self.doubleSpinBox_max.valueChanged.connect(self.parent().setmax)


    # method
    def saveState(self, settings):
        # settings.setValue("timeRange", self.doubleSpinBox_timerange.value())

        settings.setValue("frequency1", self.doubleSpinBox_frequency1.value())
        settings.setValue("frequency2", self.doubleSpinBox_frequency2.value())

        settings.setValue("RANGE_MIN", self.doubleSpinBox_min.value())
        settings.setValue("RANGE_MAX", self.doubleSpinBox_max.value())

    # method
    def restoreState(self, settings):
        frequency1 = settings.value("frequency1", DEFAULT_FREQUENCY1, type=float)
        self.doubleSpinBox_frequency1.setValue(frequency1)

        frequency2 = settings.value("frequency2", DEFAULT_FREQUENCY2, type=float)
        self.doubleSpinBox_frequency2.setValue(frequency2)

        RANGE_MIN = settings.value("RANGE_MIN", DEFAULT_MIN, type=float)
        self.doubleSpinBox_min.setValue(RANGE_MIN)

        RANGE_MAX = settings.value("RANGE_MAX", DEFAULT_MAX, type=float)
        self.doubleSpinBox_max.setValue(RANGE_MAX)
