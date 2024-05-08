import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QPushButton, QComboBox, QListWidget, \
    QListWidgetItem, QMessageBox
from PyQt6.QtGui import QPixmap, QPainter, QImage, QImageReader
from PyQt6.QtCore import Qt
import os
from PartSelect import PartSelector
from TemplateManager import FileManager
from PreviewWidget import PreviewLabel

class Graphicmaker(QWidget):
    def __init__(self, folder_path='Assets',part_name = '--', styles = '--'):
        super().__init__()
        self.setWindowTitle('Graphic Maker')
        self.setGeometry(100, 100, 600, 400)
        self.file_manager = FileManager(folder_path)
        self.part_name = part_name
        self.styles = styles
        self.style_selectors = []
        self.preview = PreviewLabel() 
        self.main_layout = QGridLayout(self)
        
        self.init_ui()

    def init_ui(self):
        self.setLayout(self.main_layout)

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
        self.style_selectors = [PartSelector('---', '---') for _ in range(12)]

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
        
        if selected_style in paths:
            image_path = paths[selected_style]  # 根据样式名称获取路径
            self.preview.update_preview(image_path)  # 更新预览
        else:
            print(f'Error: Style path not found for {selected_style}')

    # 获取已经选择的所有部件的图片路径
        selected_styles = [selector.current_style() for selector in self.style_selectors if selector.current_style()]
        composite_image = self.create_composite_image(template_name, selected_styles, paths)  # 合成图片
        self.preview.update_preview(composite_image)  # 更新预览
    
    def create_composite_image(self, template_name, selected_styles, _paths):
        composite_pixmap = QPixmap(192, 192)  # 创建一个新的画布
        composite_pixmap.fill(Qt.GlobalColor.white)  # 填充白色背景

        # 逐个绘制已选择的部件
        painter = QPainter(composite_pixmap)
        for style_name in selected_styles:
            # find a way to keep the full path for the selected parts to remove this ugly part
            parts = self.file_manager.get_part_names_for_template(template_name)
            all_paths = {}
            for part in parts:
                paths = self.file_manager.get_paths_for_style(template_name, part)
                all_paths = {**all_paths, **paths}

            if style_name in all_paths:
                image_paths = all_paths[style_name]  # 根据部件名称获取路径
                for each_path in image_paths:
                    print(os.fsdecode(each_path))
                    each_pixmap = QPixmap(os.fsdecode(each_path))  # 加载部件图片
                    if not each_pixmap.isNull():  # 检查图片是否有效
                        painter.drawPixmap(0, 0, each_pixmap)  # 将部件图片绘制到画布上
                    else:
                        print(f'Error: Invalid image for {style_name}')
            else:
                print(f'Error: Part path not found for {style_name}')
        painter.end()  # 结束绘制

        composite_image = composite_pixmap.toImage()  # 将 QPixmap 转换为 QImage
        return composite_image  # 返回合成后的图片对象
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Graphicmaker()
    window.show()
    sys.exit(app.exec())
