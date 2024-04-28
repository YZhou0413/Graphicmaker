import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QPushButton, QComboBox, QListWidget, \
    QListWidgetItem, QMessageBox
from PyQt6.QtGui import QPixmap, QPainter, QImage, QImageReader
from PyQt6.QtCore import Qt
from PartSelect import PartSelector
from TemplateManager import FileManager
from PreviewWidget import PreviewLabel


class Graphicmaker(QWidget):
    def __init__(self, folder_path='Assets', part_name='--', styles='--'):
        super().__init__()
        self.setWindowTitle('Graphic Maker')
        self.setGeometry(100, 100, 600, 400)
        self.file_manager = FileManager(folder_path)
        self.part_name = part_name
        self.styles = styles
        self.part_selectors = []
        self.preview = PreviewLabel()
        self.main_layout = QGridLayout(self)

        self.init_ui()

    def init_ui(self):
        self.setLayout(self.main_layout)

        # 初始化模板下拉选择框
        self.setup_template_combo_box()
        self.setup_preview()
        # 加载模板列表
        self.load_templates()

    def setup_preview(self):
        self.main_layout.addWidget(self.preview, 1, 2, 2, 2)

    def setup_template_combo_box(self):
        template_layout = QVBoxLayout()

        self.template_label = QLabel(f'Choose template:')
        self.template_combo_box = QComboBox()
        self.template_combo_box.currentIndexChanged.connect(self.handle_template_change)

        template_layout.addWidget(self.template_label)
        template_layout.addWidget(self.template_combo_box)
        self.main_layout.addLayout(template_layout, 0, 0, 1, 4)

        # 将模板选择部件添加到主布局中

    def load_templates(self):
        template_names = self.file_manager.get_template_names()
        self.template_combo_box.addItems(template_names)

    def handle_template_change(self):
        template_name = self.template_combo_box.currentText()
        self.clear_part_selectors()
        self.init_part_selectors()
        self.update_part_selectors(template_name)

    def clear_part_selectors(self):
        self.part_selectors = [PartSelector('---', '---') for _ in range(12)]

    def init_part_selectors(self):
        part_selector_layout_l = QGridLayout()
        part_selector_layout_r = QGridLayout()
        for i, default_selector in enumerate(self.part_selectors):
            layout = part_selector_layout_l if i < 8 else part_selector_layout_r
            row, col = divmod(i, 2)
            layout.addWidget(default_selector, row, col)
        self.main_layout.addLayout(part_selector_layout_l, 1, 0, 4, 2)
        self.main_layout.addLayout(part_selector_layout_r, 3, 2, 2, 2)

    def update_part_selectors(self, template_name):
        parts = self.file_manager.get_part_names_for_template(template_name)

        if len(parts) > 12:
            QMessageBox.warning(self, "警告", "部件数量过多！")
            return

        for i, part_name in enumerate(parts):
            if i < len(self.part_selectors):
                styles = self.file_manager.get_styles_for_part(template_name, part_name)
                paths = self.file_manager.get_paths_for_part(template_name, part_name)
                self.part_selectors[i].set_text(part_name)
                self.part_selectors[i].set_styles(styles, paths)
                self.part_selectors[i].part_selected.connect(self.handle_part_selected)
            else:
                break

    def handle_part_selected(self, part_name, selected_style):

        print(f'Selected part: {part_name}, Style: {selected_style}')
        template_name = self.template_combo_box.currentText()
        paths = self.file_manager.get_paths_for_part(template_name, part_name)

        if selected_style in paths:
            image_path = paths[selected_style]  # 根据样式名称获取路径
            self.preview.update_preview(image_path)  # 更新预览
        else:
            print(f'Error: Style path not found for {selected_style}')

        # 获取已经选择的所有部件的图片路径
        selected_styles = [selector.current_part() for selector in self.part_selectors if selector.current_part()]
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
                paths = self.file_manager.get_paths_for_part(template_name, part)
                all_paths = {**all_paths, **paths}

            if style_name in all_paths:
                image_path = all_paths[style_name]  # 根据部件名称获取路径
                part_pixmap = QPixmap(image_path)  # 加载部件图片
                if not part_pixmap.isNull():  # 检查图片是否有效
                    painter.drawPixmap(0, 0, part_pixmap)  # 将部件图片绘制到画布上
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
