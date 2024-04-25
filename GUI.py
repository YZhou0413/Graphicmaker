import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,QGridLayout, QPushButton, QComboBox, QListWidget, QListWidgetItem
from PyQt6.QtGui import QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt
from PartSelect import PartSelector
from TemplateManager import FileManager
from PreviewWidget import PreviewLabel

class Graphicmaker(QWidget):
    def __init__(self, folder_path='Assets',part_name = '--', styles = '--'):
        super().__init__()
        self.setWindowTitle('Graphic Maker')
        self.setGeometry(100, 100, 400, 300)
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
        # 清空现有的部件选择器
        self.clear_part_selectors()

        # 获取选择的模板名称
        template_name = self.template_combo_box.currentText()

        # 加载并显示部件选择器
        self.generate_part_selectors(template_name)

    def clear_part_selectors(self):
        # 清空现有的部件选择器
        for selector in self.part_selectors:
            selector.deleteLater()

        # 清空部件选择器列表
        self.part_selectors = []

    def generate_part_selectors(self, template_name):
        part_selector_layout = QGridLayout()
        # 获取部件名称列表
        parts = self.file_manager.get_part_names_for_template(template_name)

        row = 0
        col = 0

        for part_name in parts:
            # 获取部件的实际样式列表
            styles = self.file_manager.get_styles_for_part(template_name, part_name)
            part_selector = PartSelector(part_name, styles)

            # 连接部件选择器的信号
            part_selector.part_selected.connect(self.handle_part_selected)

            # 将部件选择器添加到布局中的特定位置
            part_selector_layout.addWidget(part_selector, row, col)

            # 更新列索引，每行显示两个部件选择器
            col += 1
            if col > 1:
                col = 0
                row += 1

            # 将部件选择器添加到部件选择器列表
            self.part_selectors.append(part_selector)
        self.main_layout.addLayout(part_selector_layout, 1, 0, 4, 2)


    def handle_part_selected(self, part_name, selected_style):
        print(f'Selected part: {part_name}, Style: {selected_style}')


    def update_avatar_preview(self):
        # 合成头像
        avatar_image = self.create_avatar()
        if avatar_image:
            pixmap = QPixmap.fromImage(avatar_image)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio))

    def create_avatar(self):
        avatar_image = QImage(200, 200, QImage.Format.Format_RGB888)
        avatar_image.fill(Qt.GlobalColor.gray)

        painter = QPainter(avatar_image)

        # 根据当前选择的部件样式绘制头像
        if self.avatar_parts['hair']:
            # 绘制头发
            # 示例：使用实际的绘制代码替换这里
            pass

        if self.avatar_parts['eyes']:
            # 绘制眼睛
            # 示例：使用实际的绘制代码替换这里
            pass

        if self.avatar_parts['nose']:
            # 绘制鼻子
            # 示例：使用实际的绘制代码替换这里
            pass

        if self.avatar_parts['mouth']:
            # 绘制嘴巴
            # 示例：使用实际的绘制代码替换这里
            pass

        painter.end()
        return avatar_image

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Graphicmaker()
    window.show()
    sys.exit(app.exec())