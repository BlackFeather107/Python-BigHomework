from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from controller.main_controller import MainController

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = MainController()
    window = MainWindow(controller)
    window.show()
    sys.exit(app.exec_())