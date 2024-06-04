from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QToolBar, QDockWidget, QFrame, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from GUI import Graphicmaker
from LayerManager import LayerManager
from PreviewWidget import PreviewGraphicsView
from ColorAdjust import ColorAdjuster

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("Graphic Maker")
        self.setFixedSize(1000, 700)
        #placeholder Widget
        self.LM_titel = QLabel(self)
        self.LM_titel.setStyleSheet("""
            QLabel{background: #f3f6f4;}
            QLabel{font-size:12px;}
        """    
        ) 
        self.placeholder2 = QLabel(self)
        self.placeholder3 = QLabel(self)
        self.placeholder4 = QLabel(self)
        self.placeholder5 = QLabel(self)
        self.C_Adjuster = ColorAdjuster()
        self.P_Widget = PreviewGraphicsView()
        self.L_manager = LayerManager(preview=self.P_Widget)
        self.selectors = Graphicmaker(layer_manager=self.L_manager, folder_path='Assets', part_name='--'
                             ,styles='--')
        self.setCentralWidget(self.selectors)
        self.selectors.style_layers_info.connect(self.L_manager.set_selected_styles)
        self.selectors.part_click.connect(self.L_manager.add_part_to_order)
        self.selectors.change_template.connect(self.L_manager.clear_layers_template_change)
        self.L_manager.clear_all_requested.connect(self.selectors.clear_selected)


        self.r_dock = QDockWidget(self)
        self.r_dock.setStyleSheet("QDockWidget::title { border: 0px; }")
        self.r_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.r_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.r_frame = QFrame(self)
        self.r_dock.setWidget(self.r_frame)
        r_dock_layout = QVBoxLayout()
        self.r_frame.setLayout(r_dock_layout)
        r_dock_layout.addWidget(self.P_Widget)
        r_dock_layout.addWidget(self.L_manager)

        #set up dock widgets(frames)
        self.d_dock = QDockWidget(self)
        self.d_dock.setFixedWidth(600)
        self.d_dock.setStyleSheet("QDockWidget::title { border: 0px; }")
        self.d_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.d_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.d_frame = QFrame(self)
        self.d_dock.setWidget(self.d_frame)
        d_dock_layout = QHBoxLayout()
        self.d_frame.setLayout(d_dock_layout)
        d_dock_layout.addWidget(self.C_Adjuster)
        d_dock_layout.addWidget(self.placeholder2)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.d_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.r_dock)
        

        self.test_button = QPushButton("Test Button", self)
        self.test_button.setGeometry(10, 10, 100, 30)
        self.test_button.clicked.connect(self.test_button_clicked)
        self.setup_Toolbar()

    def test_button_clicked(self):
        print("Test Button Clicked")

        

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
