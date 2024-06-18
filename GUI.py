import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QPushButton, QComboBox, QListWidget, \
    QListWidgetItem, QMessageBox
from PyQt6.QtGui import QPixmap, QPainter, QImage, QImageReader
from PyQt6.QtCore import Qt, pyqtSignal
import os
from PartSelect import PartSelector
from FileManager import FileManager
from PreviewWidget import PreviewGraphicsView
from LayerManager import LayerManager
from collections import defaultdict

class Graphicmaker(QWidget):
    style_layers_info = pyqtSignal(defaultdict)
    part_click = pyqtSignal(str)
    change_template = pyqtSignal(str)
    set_style_data_sig = pyqtSignal(str, defaultdict)
    
    def __init__(self, layer_manager, folder_path, part_name = '--', styles = '--'):
        super().__init__()
        self.setWindowTitle('Graphic Maker')
        self.setGeometry(100, 100, 600, 400)
        self.file_manager = FileManager(folder_path)
        self.folder_path = folder_path
        self.part_name = part_name
        self.styles = styles
        self.style_selectors = [] 
        self.main_layout = QGridLayout(self)
        self.layer_manager = layer_manager
        self.init_ui()

    def load_new_folder(self, source_path):
        self.file_manager.update_folder_path(source_path)
        self.load_templates()

    def init_ui(self):
        self.setLayout(self.main_layout)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 0, 0)  

        self.setup_template_combo_box()
        self.load_templates()

    def setup_template_combo_box(self):
        template_layout = QVBoxLayout()

        self.template_label = QLabel(f'Choose template:')
        self.template_combo_box = QComboBox()
        self.template_combo_box.currentIndexChanged.connect(self.react_template_change)

        template_layout.addWidget(self.template_label)
        template_layout.addWidget(self.template_combo_box)
        self.main_layout.addLayout(template_layout, 0, 0, 1, 3)
     
    def load_templates(self):
        self.template_combo_box.clear()
        template_names = self.file_manager.get_template_names()
        self.template_combo_box.addItems(template_names)

    def react_template_change(self):
        template_name = self.template_combo_box.currentText()
        self.clear_style_selectors()
        self.init_style_selectors()
        self.update_style_selectors(template_name)
        self.change_template.emit(template_name)

    def clear_style_selectors(self):
        for i in self.style_selectors:
            i.deleteLater()
        self.style_selectors = [PartSelector('', '') for _ in range(12)]

    def init_style_selectors(self):
        part_selector_layout = QGridLayout()
        for i, default_selector in enumerate(self.style_selectors):
            layout = part_selector_layout
            row, col = divmod(i, 3)
            layout.addWidget(default_selector, row, col)
        self.main_layout.addLayout(part_selector_layout, 1, 0, 4, 3)


    def update_style_selectors(self, template_name):
        parts = self.file_manager.get_part_names_for_template(template_name)

        if len(parts) > 12:
            QMessageBox.warning(self, "Warning", "Too Many Parts!")
            return

        for i, part_name in enumerate(parts):
            if i < len(self.style_selectors):
                styles = self.file_manager.remove_dosign(template_name, part_name)
                self.style_selectors[i].set_text(part_name)
                self.style_selectors[i].set_styles(styles)
                self.style_selectors[i].style_chosen.connect(self.react_style_selected)
            else:
                break

    def clear_selected(self):
        for style_selector in self.style_selectors:
            style_selector.clear_item_select()
        self.style_layers_info.emit({})
        
    def random_selection(self):
        self.clear_selected()
        for style_selector in self.style_selectors:
            style_selector.random_select()


    def react_style_selected(self, part_name, selected_style):
        print(f'Selected part: {part_name}, Style: {selected_style}')
        template_name = self.template_combo_box.currentText()
        object_needed = self.file_manager.create_object_for_style(template_name, part_name, selected_style)
        self.style_layers_info.emit(object_needed)
        self.part_click.emit(part_name)
        for selector in self.style_selectors:
            if part_name == selector.part_name:
                selector.set_item_data(selected_style, object_needed)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Graphicmaker()
    window.show()
    sys.exit(app.exec())
