import cv2

from core.black_saver import BlackSaver

from core.analyzer import GraphicAnalyzer

import sys

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

from PySide6.QtWidgets import QSlider

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())