from PyQt5.QtWidgets import *
from src.qt_app import Widget
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Widget(app)
    w.show()
    sys.exit(app.exec_())
