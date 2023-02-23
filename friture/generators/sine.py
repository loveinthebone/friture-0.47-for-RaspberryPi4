#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

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

import numpy as np
from PyQt5 import QtWidgets

DEFAULT_SINE_FREQUENCY = 6000.
DEFAULT_SINE_FREQUENCY1 = 6200.


class SineGenerator:

    name = "Sine"

    def __init__(self, parent):
        self.f = 6000.
        self.f1 = 6200.
        self.settings = SettingsWidget(parent)
        self.settings.spinBox_sine_frequency.valueChanged.connect(self.setf)
        self.settings.spinBox_sine_frequency1.valueChanged.connect(self.setf1)
        self.offset = 0
        self.offset1 = 0
        self.lastt = 0
        self.lastt1 = 0

    def setf(self, f):
        oldf = self.f
        self.f = f

        # the offset is adapted to avoid phase break
        lastphase = 2. * np.pi * self.lastt * oldf + self.offset
        newphase = 2. * np.pi * self.lastt * self.f + self.offset
        self.offset += (lastphase - newphase)
        self.offset %= 2. * np.pi   #I guess here just make the phase smaller than 2*pi

    def setf1(self, f1):
        oldf1 = self.f1
        self.f1 = f1

        # the offset is adapted to avoid phase break
        lastphase1 = 2. * np.pi * self.lastt1 * oldf1 + self.offset1
        newphase1 = 2. * np.pi * self.lastt1 * self.f1 + self.offset1
        self.offset1 += (lastphase1 - newphase1)
        self.offset1 %= 2. * np.pi   #I guess here just make the phase smaller than 2*pi

    def settingsWidget(self):
        return self.settings

    def signal(self, t):
        self.lastt = t[-1]
        return 0.2*np.sin(2. * np.pi * t * self.f + self.offset) 
        # + np.sin(2. * np.pi * t * (50+self.f) + self.offset)

    def signal1(self, t):
        self.lastt1 = t[-1]
        return 0.2*np.sin(2. * np.pi * t * (self.f1) + self.offset1) 
        # + np.sin(2. * np.pi * t * (50+self.f) + self.offset)

class SettingsWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.spinBox_sine_frequency = QtWidgets.QDoubleSpinBox(self)
        self.spinBox_sine_frequency.setKeyboardTracking(False)
        self.spinBox_sine_frequency.setDecimals(2)
        self.spinBox_sine_frequency.setSingleStep(1)
        self.spinBox_sine_frequency.setMinimum(20)
        self.spinBox_sine_frequency.setMaximum(22000)
        self.spinBox_sine_frequency.setProperty("value", DEFAULT_SINE_FREQUENCY)
        self.spinBox_sine_frequency.setObjectName("spinBox_sine_frequency")
        self.spinBox_sine_frequency.setSuffix(" Hz")
  
        self.spinBox_sine_frequency1 = QtWidgets.QDoubleSpinBox(self)
        self.spinBox_sine_frequency1.setKeyboardTracking(False)
        self.spinBox_sine_frequency1.setDecimals(2)
        self.spinBox_sine_frequency1.setSingleStep(1)
        self.spinBox_sine_frequency1.setMinimum(20)
        self.spinBox_sine_frequency1.setMaximum(22000)
        self.spinBox_sine_frequency1.setProperty("value", DEFAULT_SINE_FREQUENCY)
        self.spinBox_sine_frequency1.setObjectName("spinBox_sine_frequency1")
        self.spinBox_sine_frequency1.setSuffix(" Hz")
        # self.spinBox_sine_frequency1.set

        # self.formLayout = QtWidgets.QFormLayout(self)
        self.qhboxlayout = QtWidgets.QHBoxLayout(self)
       
        self.qhboxlayout.addWidget(self.spinBox_sine_frequency)
        
        self.qhboxlayout.addWidget(self.spinBox_sine_frequency1)

        # self.qhboxlayout.addRow("Frequency 1:", self.spinBox_sine_frequency)
        # self.qhboxlayout.addRow(self.spinBox_sine_frequency,self.spinBox_sine_frequency1)

        # self.qhboxlayout.addRow(, )
        # self.qhboxlayout.add

        self.setLayout(self.qhboxlayout)

    def saveState(self, settings):
        settings.setValue("sine frequency", self.spinBox_sine_frequency.value())
        settings.setValue("sine frequency1", self.spinBox_sine_frequency1.value())

    def restoreState(self, settings):
        sine_freq = settings.value("sine frequency", DEFAULT_SINE_FREQUENCY, type=float)
        self.spinBox_sine_frequency.setValue(sine_freq)
        sine_freq1 = settings.value("sine frequency1", DEFAULT_SINE_FREQUENCY1, type=float)
        self.spinBox_sine_frequency1.setValue(sine_freq1)
