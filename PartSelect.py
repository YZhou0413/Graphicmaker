from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt

class PartSelector(QWidget):
    part_selected = pyqtSignal(str, str)  # 自定义信号，传递部件类型和所选样式

    def __init__(self, part_name, styles, parent=None):
        super().__init__(parent)
        self.part_name = part_name
        self.styles = styles
        self.block_layout = QVBoxLayout()
        self.setup_ui()
        

    def setup_ui(self):
        self.setLayout(self.block_layout)
        self.label = QLabel(f'{self.part_name}:', self)
        self.list_widget = QListWidget(self)
        self.block_layout.addWidget(self.label)

        for style in self.styles:
            item = QListWidgetItem(style)
            self.list_widget.addItem(item)
        self.list_widget.itemClicked.connect(self.handle_item_click)
        self.block_layout.addWidget(self.list_widget)

    def handle_item_click(self, item):
        if isinstance(item, QListWidgetItem):  # 确保 item 是 QListWidgetItem 类型
            selected_style = item.text()  # 获取所选项的文本
            self.part_selected.emit(self.part_name, selected_style)  # 发送部件选择信号
        else:
            print("Invalid item type:", type(item))

