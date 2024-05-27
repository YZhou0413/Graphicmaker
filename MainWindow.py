from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QToolBar, QDockWidget, QFrame, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from GUI import Graphicmaker
from LayerManager import LayerManager
from PreviewWidget import PreviewGraphicsView


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("Graphic Maker")
        self.resize(1000, 700)
        #placeholder Widget
        self.LM_titel = QLabel(self)
        self.LM_titel.setStyleSheet("""
            QLabel{background: #f3f6f4;}
            QLabel{font-size:12px;}
        """    
        ) 
        self.LM_titel.setText("Layer Manager")
        self.placeholder1 = QLabel(self)
        self.placeholder2 = QLabel(self)
        self.placeholder3 = QLabel(self)
        self.placeholder4 = QLabel(self)
        self.placeholder5 = QLabel(self)
        self.P_Widget = PreviewGraphicsView()
        self.L_manager = LayerManager(preview=self.P_Widget)
        self.selectors = Graphicmaker(layer_manager=self.L_manager, folder_path='Assets', part_name='--'
                             ,styles='--')
        self.setCentralWidget(self.selectors)
        self.selectors.style_layers_info.connect(self.L_manager.set_selected_styles)

        #set up dock widgets(frames)
        self.l_dock = QDockWidget(self)
        self.l_frame = QFrame(self)
        self.l_dock.setWidget(self.l_frame)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.l_dock)
        l_dock_layout = QVBoxLayout()
        self.l_frame.setLayout(l_dock_layout)
        l_dock_layout.addWidget(self.placeholder1, 3)
        l_dock_layout.addWidget(self.placeholder2, 3)

        self.r_dock = QDockWidget(self)
        self.r_frame = QFrame(self)
        self.r_dock.setWidget(self.r_frame)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.r_dock)
        r_dock_layout = QVBoxLayout()
        self.r_frame.setLayout(r_dock_layout)
        r_dock_layout.addWidget(self.P_Widget, 3)
        r_dock_layout.addWidget(self.LM_titel)
        r_dock_layout.addWidget(self.L_manager, 3)


        self.setup_Toolbar()

    def setup_Toolbar(self):
        menu = self.menuBar()
        File = menu.addMenu('File')
        File.addAction('New')
        SaveA = File.addMenu('Save as')
        SaveA.addAction('*.PNG')
        SaveA.addAction('*.JPG')
        QuitAct = QAction("Quit", self)
        QuitAct.triggered.connect(self.close)
        menu.addAction(QuitAct)

        




    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec())
