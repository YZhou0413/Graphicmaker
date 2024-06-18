from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QToolBar, QDockWidget, QFrame, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton, QFileDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal
from GUI import Graphicmaker
from LayerManager import LayerManager
from PreviewWidget import PreviewWidget
from ColorAdjust import ColorAdjuster
from Exporter import exporter

class Ui_MainWindow(QMainWindow):
    new_folder = pyqtSignal(str)
    random = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setObjectName("Graphic Maker")
        self.setFixedSize(1000, 700)

        self.C_Adjuster = ColorAdjuster()
        self.P_Widget = PreviewWidget()
        self.L_manager = LayerManager(preview=self.P_Widget)
        self.selectors = Graphicmaker(layer_manager=self.L_manager, folder_path='Assets', part_name='--'
                             ,styles='--')
        self.exporter = exporter()
        self.setCentralWidget(self.selectors)
        
        self.random.connect(self.selectors.random_selection)
        self.new_folder.connect(self.selectors.load_new_folder)
        self.selectors.style_layers_info.connect(self.L_manager.set_selected_styles)
        self.selectors.part_click.connect(self.L_manager.add_part_to_order)
        self.selectors.change_template.connect(self.L_manager.clear_layers_template_change)
        self.L_manager.clear_all_requested.connect(self.selectors.clear_selected)
        self.L_manager.update_preview_dict.connect(self.P_Widget.pre_view.update_preview)
        self.C_Adjuster.hsba_changed.connect(self.L_manager.update_color_adjustments)
        self.exporter.bg_color_bool.connect(self.C_Adjuster.mani_signal_connection)
        self.C_Adjuster.bg_color.connect(self.P_Widget.pre_view.change_bg_color)
        self.exporter.save_bg_bool.connect(self.P_Widget.pre_view.save_image_png_bg)
        self.exporter.bg_pic.connect(self.P_Widget.pre_view.bg_pic)


        self.r_dock = QDockWidget(self)
        self.r_dock.setStyleSheet("QDockWidget::title { border: 0px; }")
        self.r_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.r_dock.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.r_frame = QFrame(self)
        self.r_frame.setFixedWidth(450)
        self.r_dock.setWidget(self.r_frame)
        r_dock_layout = QGridLayout()
        self.r_frame.setLayout(r_dock_layout)
        r_dock_layout.addWidget(self.P_Widget, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        r_dock_layout.addWidget(self.L_manager, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        r_dock_layout.addWidget(self.C_Adjuster, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        r_dock_layout.addWidget(self.exporter, 1, 1, alignment=Qt.AlignmentFlag.AlignTop)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.r_dock)
        self.setup_Toolbar()

    def setup_Toolbar(self):
        menu = self.menuBar()
        File = menu.addMenu('File')
        File.addAction('New')
        source = File.addAction('load folder')
        source.triggered.connect(self.set_source_path)
        SaveA = File.addMenu('Save as')
        with_bg = SaveA.addAction('*.PNG with background')
        with_bg.triggered.connect(self.exporter.save_bg_signal_true)
        no_bg = SaveA.addAction('*.PNG without background')
        no_bg.triggered.connect(self.exporter.save_bg_signal_false)
        HelpAct = QAction("Help", self)
        QuitAct = QAction("Quit", self)
        RandomAct = QAction("Randomizer", self)
        RandomAct.triggered.connect(self.throw_random)
        QuitAct.triggered.connect(self.close)
        menu.addAction(RandomAct)
        menu.addAction(HelpAct)
        menu.addAction(QuitAct)

    def set_source_path(self):
        new_folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.new_folder.emit(new_folder_path)
        
    def throw_random(self):
        self.random.emit()
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec())
