
from PyQt5 import QtWidgets
import sys

from config import *
from ui_main_window import MainWindow
from main_controller import MainController



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    main_controller = MainController(window)
    window.show()
    sys.exit(app.exec_())