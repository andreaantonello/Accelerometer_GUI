from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout,
                             QLabel, QSizePolicy, QSlider, QSpacerItem,
                             QVBoxLayout, QWidget)

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

from numba import jit, prange, njit
import numpy as np

from pathlib import Path
import sys

from time import time
import types


from src import read_serial


colors = {
    'lightest': "#eeeeee",
    'lighter': "#e5e5e5",
    'light': "#effffb",
    'himid': "#50d890",
    'midmid': "#1089ff",
    'lomid': "#4f98ca",
    'dark': "#272727",
    'darker': "#23374d",
}

numlabelsize = 22
txtlabelsize = 20

# STYLING
numfont = QtGui.QFont("Avenir Next")  # requires macos
numfont.setPixelSize(numlabelsize)

txtfont = QtGui.QFont("Avenir Next")  # requires macos
txtfont.setPixelSize(txtlabelsize)

brushes = {k: pg.mkBrush(c) for k, c in colors.items()}

pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', colors['dark'])
pg.setConfigOption('foreground', colors['light'])

QPushButton_style = f"""
QPushButton{{
	color: {colors['light']};
	background-color: transparent;
	border: 1px solid #4589b2;
	padding: 5px;
}}
QPushButton::hover{{
	background-color: rgba(255,255,255,.2);
}}
QPushButton::pressed{{
	border: 1px solid {colors['himid']};
	background-color: rgba(0,0,0,.3);
}}"""

QLabel_style = f"""
QLabel{{
    color: {colors['light']};
}}
"""

QCheckBox_style = f"""
QCheckBox{{
    background-color: {colors['darker']};
    color: {colors['light']};
    padding:5px;
}}
"""


class Controls(QWidget):
    def __init__(self, variable='', parent=None):
        super(Controls, self).__init__(parent=parent)
        self.horizontalLayout = QHBoxLayout(self)

        self.l1 = QHBoxLayout()
        self.l1.setAlignment(Qt.AlignTop)

        self.pause = QtWidgets.QPushButton('Pause', parent=self)
        self.l1.addWidget(self.pause)

        self.clear = QtWidgets.QPushButton('Clear', parent=self)
        self.clear.setCheckable(False)
        self.l1.addWidget(self.clear)

        self.horizontalLayout.addLayout(self.l1)

        # STYLING
        self.clear.setStyleSheet(QPushButton_style)
        self.pause.setStyleSheet(QPushButton_style)


class Widget(QWidget):
    def __init__(self, app, parent=None):
        super(Widget, self).__init__(parent=parent)

        self.arduino = read_serial.ArduinoInterface()
        self.arduino.get_arduino_uno_port()

        self.setStyleSheet(f"Widget {{ background-color: {colors['dark']}; }}")

        self.app = app

        self.horizontalLayout = QVBoxLayout(self)
        self.controls = Controls(parent=self)

        self.horizontalLayout.addWidget(self.controls)

        self.win = pg.GraphicsWindow()

        self.setWindowTitle('MPU9250 data')
        self.horizontalLayout.addWidget(self.win)

        self.plots = [self.win.addPlot(row=1, col=1, title="Acc x", labels={'left': "[rad/s^2]", 'bottom': "Time [s]"}),
                      self.win.addPlot(row=2, col=1, title="Acc y", labels={'left': "[rad/s^2]", 'bottom': "Time [s]"}),
                      self.win.addPlot(row=3, col=1, title="Acc z", labels={'left': "[rad/s^2]", 'bottom': "Time [s]"}),
                      self.win.addPlot(row=1, col=2, title="Gyro x", labels={'left': "[rad/s]", 'bottom': "Time [s]"}),
                      self.win.addPlot(row=2, col=2, title="Gyro y", labels={'left': "[rad/s]", 'bottom': "Time [s]"}),
                      self.win.addPlot(row=3, col=2, title="Gyro z", labels={'left': "[rad/s]", 'bottom': "Time [s]"}),
                      self.win.addPlot(row=1, col=3, title="Mag x", labels={'left': "[rad/s^2]", 'bottom': "Time [s]"}),
                      self.win.addPlot(row=2, col=3, title="Mag y", labels={'left': "[rad/s^2]", 'bottom': "Time [s]"}),
                      self.win.addPlot(row=3, col=3, title="Mag z", labels={'left': "[rad/s^2]", 'bottom': "Time [s]"}),
                      ]

        self.timer = QtCore.QTimer()

        self.controls.clear.pressed.connect(self.clear)
        self.controls.pause.pressed.connect(self.pause)

    def clear(self):
        print('Clear')

    def pause(self):
        print('Pause')

    def reset(self):
        print('Reset')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Widget(app)
    w.show()
    sys.exit(app.exec_())
