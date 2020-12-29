from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget, QGridLayout
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import time
from src import read_serial


PLOT_NAMES = ['Acc x', 'Acc y', 'Acc z', 'Gyro x', 'Gyro y', 'Gyro z', 'Mag x', 'Mag y', 'Mag z']
PLOT_X_LABEL = ['Time [s]']*9
PLOT_Y_LABEL = ['[g]', '[g]', '[g]', '[rad/s]', '[rad/s]', '[rad/s]', '[uT]', '[uT]', '[uT]']
N_SAMPLES = 300

colors = {
    'lightest': "#eeeeee",
    'lighter': "#e5e5e5",
    'light': "#effffb",
    'light_gray': "#898989",
    'hi_mid': "#50d890",
    'mid_mid': "#1089ff",
    'lo_mid': "#4f98ca",
    'dark': "#272727",
    'darker': "#23374d",
}

brushes = {k: pg.mkBrush(c) for k, c in colors.items()}

pg.setConfigOptions(antialias=True)
pg.setConfigOption('background', colors['dark'])
pg.setConfigOption('foreground', colors['light_gray'])

QPushButton_style = f"""QPushButton{{color: {colors['light_gray']}; background-color: transparent; 
border: 1px solid #4589b2; padding: 5px;}} QPushButton::hover{{background-color: rgba(255,255,255,.2);}}
QPushButton::pressed{{border: 1px solid {colors['light_gray']}; background-color: rgba(0,0,0,.3);}}"""

QLabel_style = f"""QLabel{{color: {colors['light_gray']};}}"""
QCheckBox_style = f"""QCheckBox{{background-color: {colors['darker']}; color: {colors['light_gray']}; padding:5px;}}"""


class Controls(QWidget):
    def __init__(self, parent=None):
        super(Controls, self).__init__(parent=parent)
        self.horizontalLayout = QHBoxLayout(self)

        # Set-up buttons
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

        # Set-up styling
        self.start_pause.setStyleSheet(QPushButton_style)
        self.clear.setStyleSheet(QPushButton_style)
        self.quit.setStyleSheet(QPushButton_style)


class Widget(QWidget):
    def __init__(self, app, parent=None):
        super(Widget, self).__init__(parent=parent)

        # Set-up PyQt window
        self.setWindowTitle('MPU9250 Data Acquisition')
        self.setStyleSheet(f"Widget {{ background-color: {colors['dark']}; }}")
        self.showMaximized()

        # Set-up layout
        self.app = app
        self.gridLayout = QGridLayout(self)
        self.controls = Controls(parent=self)
        self.gridLayout.addWidget(self.controls)
        self.win = pg.GraphicsWindow()
        self.gridLayout.addWidget(self.win)

        # Initialise variables
        self.pause = True
        self.clear_all = False
        self.serial_communication = None
        self.plot = []
        self.curve = []
        self.data1 = np.zeros((3, N_SAMPLES))  # contains acc_x, acc_y and acc_z
        self.data2 = np.zeros((3, N_SAMPLES))  # contains gyr_x, gyr_y and gyr_z
        self.data3 = np.zeros((3, N_SAMPLES))  # contains mag_x, mag_y and mag_z
        self.initialise_plots()
        self.tps = np.zeros(10)  # you need time to, the same length as data

        # Initialise timer
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(5)

        # Set-up buttons
        self.controls.start_pause.pressed.connect(self.start_pause_button)
        self.controls.clear.pressed.connect(self.clear)
        self.controls.quit.pressed.connect(self.quit)

    def initialise_plots(self):
        for index in range(9):
            self.plot.append(self.win.addPlot(row=index % 3 + 1, col=index // 3 + 1, title=PLOT_NAMES[index],
                                              labels={'bottom': PLOT_X_LABEL[index], 'left': PLOT_Y_LABEL[index]},
                                              pen={'color': 'k', 'cosmetic': False}))
            self.curve.append(self.plot[index].plot(self.data1[0]))

    def clear(self):
        self.clear_all = True
        self.data1 = np.hstack([np.reshape(self.data1[:, -1], (3, 1))] * N_SAMPLES)  # contains acc_x, acc_y and acc_z
        self.data2 = np.hstack([np.reshape(self.data2[:, -1], (3, 1))] * N_SAMPLES)  # contains gyr_x, gyr_y and gyr_z
        self.data3 = np.hstack([np.reshape(self.data3[:, -1], (3, 1))] * N_SAMPLES)  # contains mag_x, mag_y and mag_z

    def update(self):
        if not self.serial_communication:
            self.serial_communication = read_serial.ArduinoInterface()
        split_string = self.serial_communication.decode_serial()

        if split_string and not self.pause:
            start = time.time()
            acc = split_string[0:3]
            gyr = split_string[3:6]
            mag = split_string[6:9]
            self.data1[:, :-1] = self.data1[:, 1:]  # shift data in the array one sample left
            self.data2[:, :-1] = self.data2[:, 1:]
            self.data3[:, :-1] = self.data3[:, 1:]

            self.data1[:, -1] = acc
            self.data2[:, -1] = gyr
            self.data3[:, -1] = mag
            for axis in range(3):
                self.curve[axis].setData(self.data1[axis], pen={'color': colors['hi_mid']})
                self.curve[axis + 3].setData(self.data2[axis], pen={'color': colors['mid_mid']})
                self.curve[axis + 6].setData(self.data3[axis], pen={'color': colors['lo_mid']})
            self.app.processEvents()

    def start_pause_button(self):
        self.pause = not self.pause

    def quit(self):
        self.close()
