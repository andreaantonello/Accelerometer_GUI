from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout,
                             QLabel, QSizePolicy, QSlider, QSpacerItem,
                             QVBoxLayout, QWidget, QGridLayout)

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import sys
import time
import serial


from src import read_serial

PLOT_NAMES = ['Acc x', 'Acc y', 'Acc z', 'Gyro x', 'Gyro y', 'Gyro z', 'Mag x', 'Mag y', 'Mag z']
PLOT_XLABEL = ['Time [s]', 'Time [s]', 'Time [s]', 'Time [s]', 'Time [s]', 'Time [s]', 'Time [s]', 'Time [s]',
               'Time [s]']
PLOT_YLABEL = ['[rad/s^2]', '[rad/s^2]', '[rad/s^2]', '[rad/s]', '[rad/s]', '[rad/s]', '[rad/s^2]', '[rad/s^2]',
               '[rad/s^2]']
N_SAMPLES = 300
tps = np.zeros(N_SAMPLES)  # you need time to, the same length as data
data1 = np.zeros((3, N_SAMPLES))  # contains acc_x, acc_y and acc_z
data2 = np.zeros((3, N_SAMPLES))  # contains gyr_x, gyr_y and gyr_z
data3 = np.zeros((3, N_SAMPLES))  # contains mag_x, mag_y and mag_z

arduino = read_serial.ArduinoInterface()
com = arduino.get_arduino_uno_port()
speed = 19200
start = time.time()


colors = {
    'lightest': "#eeeeee",
    'lighter': "#e5e5e5",
    'light': "#effffb",
    'light_gray': "#898989",
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
pg.setConfigOption('foreground', colors['light_gray'])

QPushButton_style = f"""
QPushButton{{
	color: {colors['light_gray']};
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
    color: {colors['light_gray']};
}}
"""

QCheckBox_style = f"""
QCheckBox{{
    background-color: {colors['darker']};
    color: {colors['light_gray']};
    padding:5px;
}}
"""


class Controls(QWidget):
    def __init__(self, variable='', parent=None):
        super(Controls, self).__init__(parent=parent)
        self.horizontalLayout = QHBoxLayout(self)

        self.l1 = QGridLayout()

        self.start_pause = QtWidgets.QPushButton('Start/Pause', parent=self)
        self.start_pause.setCheckable(True)
        self.l1.addWidget(self.start_pause, 0, 0)

        self.clear = QtWidgets.QPushButton('Clear', parent=self)
        self.clear.setCheckable(True)
        self.l1.addWidget(self.clear, 0, 1)

        self.quit = QtWidgets.QPushButton('Quit', parent=self)
        self.quit.setCheckable(True)
        self.l1.addWidget(self.quit, 0, 2)

        self.horizontalLayout.addLayout(self.l1)

        # STYLING
        self.start_pause.setStyleSheet(QPushButton_style)
        self.clear.setStyleSheet(QPushButton_style)
        self.quit.setStyleSheet(QPushButton_style)


try:
    serie = serial.Serial(com, speed)
except:
    print("An error occured: unable to open the specified port " + com)
    exit(0)


class Widget(QWidget):
    def __init__(self, app, parent=None):
        super(Widget, self).__init__(parent=parent)

        self.setWindowTitle('MPU9250 data')
        self.setStyleSheet(f"Widget {{ background-color: {colors['dark']}; }}")

        self.app = app
        self.showMaximized()
        self.gridLayout = QGridLayout(self)

        self.controls = Controls(parent=self)

        self.gridLayout.addWidget(self.controls)

        self.win = pg.GraphicsWindow()

        self.gridLayout.addWidget(self.win)
        self.pause = True
        self.clear_all = False

        self.plot = []
        self.curve = []
        self.initialise_plots()

        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(5)

        self.data1 = np.zeros((3, N_SAMPLES))  # contains acc_x, acc_y and acc_z
        self.data2 = np.zeros((3, N_SAMPLES))  # contains gyr_x, gyr_y and gyr_z
        self.data3 = np.zeros((3, N_SAMPLES))  # contains mag_x, mag_y and mag_z

        self.controls.start_pause.pressed.connect(self.start_pause_button)
        self.controls.clear.pressed.connect(self.clear)
        self.controls.quit.pressed.connect(self.quit)

    def initialise_plots(self):
        for index in range(9):
            self.plot.append(self.win.addPlot(row=index % 3 + 1, col=index // 3 + 1, title=PLOT_NAMES[index],
                                              labels={'bottom': PLOT_XLABEL[index], 'left': PLOT_YLABEL[index]}, pen={'color':'k', 'cosmetic':False}))
            self.curve.append(self.plot[index].plot(data1[0]))

    def clear(self):
        self.clear_all = True
        self.data1 = np.hstack([np.reshape(self.data1[:, -1], (3, 1))] * N_SAMPLES)  # contains acc_x, acc_y and acc_z
        self.data2 = np.hstack([np.reshape(self.data2[:, -1], (3, 1))] * N_SAMPLES)  # contains gyr_x, gyr_y and gyr_z
        self.data3 = np.hstack([np.reshape(self.data3[:, -1], (3, 1))] * N_SAMPLES)  # contains mag_x, mag_y and mag_z

    def update(self):
        line = str(serie.readline(), 'utf-8')
        split_string = line.split(",")
        if split_string and not self.pause:
            start = time.time()
            acc = split_string[0:3]
            gyr = split_string[3:6]
            mag = split_string[6:9]
            tps[:-1] = tps[1:]
            tps[-1] = time.time() - start
            self.data1[:, :-1] = self.data1[:, 1:]  # shift data in the array one sample left
            self.data2[:, :-1] = self.data2[:, 1:]
            self.data3[:, :-1] = self.data3[:, 1:]

            self.data1[:, -1] = acc
            self.data2[:, -1] = gyr
            self.data3[:, -1] = mag
            for axis in range(3):
                self.curve[axis].setData(self.data1[axis], pen={'color': "#50d890"})
                self.curve[axis+3].setData(self.data2[axis], pen={'color': "#1089ff"})
                self.curve[axis+6].setData(self.data3[axis], pen={'color': "#4f98ca"})
            self.app.processEvents()

    def start_pause_button(self):
        self.pause = not self.pause

    def quit(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Widget(app)
    w.show()
    sys.exit(app.exec_())
