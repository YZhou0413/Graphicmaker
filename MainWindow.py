from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QToolBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from GUI import Graphicmaker


class Ui_MainWindow(QMainWindow):
    def __init__(self, selectors):
        super().__init__()
        self.setupUi(selectors)
        

    def setupUi(self, selectors):
        self.setObjectName("Graphic Maker")
        self.resize(981, 835)
        self.layout = QGridLayout()
        self.setCentralWidget(selectors)
        self.setupToolbar()
    def setupToolbar(self):
        menu = self.menuBar()
        File = menu.addMenu('File')
        File.addAction('New')
        SaveA = File.addMenu('Save as')
        SaveA.addAction('*.PNG')
        SaveA.addAction('*.JPG')
        




    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    selectors = Graphicmaker(folder_path='Assets', part_name='--'
                             ,styles='--')
    MainWindow = Ui_MainWindow(selectors)
    MainWindow.show()
    sys.exit(app.exec())
