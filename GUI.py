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
    style_layers_info = pyqtSignal(dict)
    part_click = pyqtSignal(str)
    
    
    def __init__(self, layer_manager, folder_path='Assets',part_name = '--', styles = '--'):
        super().__init__()
        self.setWindowTitle('Graphic Maker')
        self.setGeometry(100, 100, 600, 400)
        self.file_manager = FileManager(folder_path)
        self.part_name = part_name
        self.styles = styles
        self.style_selectors = [] 
        self.main_layout = QGridLayout(self)
        self.layer_manager = layer_manager
        self.init_ui()

    def init_ui(self):
        self.setLayout(self.main_layout)
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(5, 10, 0, 0)  

        # 初始化模板下拉选择框
        self.setup_template_combo_box()
        # 加载模板列表
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
        template_names = self.file_manager.get_template_names()
        self.template_combo_box.addItems(template_names)

    def react_template_change(self):
        template_name = self.template_combo_box.currentText()
        self.clear_style_selectors()
        self.init_style_selectors()
        self.update_style_selectors(template_name)

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
                paths = self.file_manager.get_paths_for_style(template_name, part_name)
                self.style_selectors[i].set_text(part_name)
                self.style_selectors[i].set_styles(styles, paths)
                self.style_selectors[i].style_chosen.connect(self.react_style_selected)
            else:
                break


    def react_style_selected(self, part_name, selected_style):
        print(f'Selected part: {part_name}, Style: {selected_style}')
        template_name = self.template_combo_box.currentText()
        paths = self.file_manager.get_paths_for_style(template_name, part_name)
        self.part_click.emit(part_name)
        if selected_style in paths:
            image_path = paths[selected_style]
            self.send_layers_with_selected_style()
        else:
            print(f'Error: Style path not found for {selected_style}')

    def send_layers_with_selected_style(self):
        # 获取已经选择的所有部件的图片路径
        selected_styles = [selector.current_style() for selector in self.style_selectors if selector.current_style()]
        template_name = self.template_combo_box.currentText()
        name_for_layers = self.collect_image_paths(template_name, selected_styles)
        self.style_layers_info.emit(name_for_layers)

    def collect_image_paths(self, template_name, selected_styles):
        name_for_layers = defaultdict(list)
        for style_name in selected_styles:
            parts = self.file_manager.get_part_names_for_template(template_name)
            all_paths = {}
            for part in parts:
                part_paths = self.file_manager.get_paths_for_style(template_name, part)
                all_paths = {**all_paths, **part_paths}
            
            if style_name in all_paths:
                image_paths = all_paths[style_name]
                for each_path in image_paths:
                    path_string = os.fsdecode(each_path)
                    layer_info = path_string.split("\\")
                    style_layer = layer_info[-1]
                    if layer_info[0] == 'None':
                        part_layer = 'None'
                    else:
                        part_layer = layer_info[-2]
                    name_for_layers[part_layer].append({style_layer: path_string})
            else:
                print(f'Error: Part path not found for {style_name}')
        return name_for_layers
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Graphicmaker()
    window.show()
    sys.exit(app.exec())
