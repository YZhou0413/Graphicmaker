from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt

class PartSelector(QWidget):
    style_chosen = pyqtSignal(str, str)  # 自定义信号，传递部件类型和所选样式

    def __init__(self, part_name, _styles, parent=None):
        super().__init__(parent)
        self.part_name = part_name
        self.styles = {}
        self.block_layout = QVBoxLayout()
        self.setup_ui()
        

    def setup_ui(self):
        self.setLayout(self.block_layout)
        self.label = QLabel(f'{self.part_name}:', self)
        self.list_widget = QListWidget(self)
        self.block_layout.addWidget(self.label)

        for style in self.styles:
            item_text = str(style)
            item_data = style["path"]
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, item_data )
            self.list_widget.addItem(item)
        self.list_widget.itemClicked.connect(self.react_item_click)
        self.block_layout.addWidget(self.list_widget)

    def react_item_click(self, item):
        if isinstance(item, QListWidgetItem):  # 确保 item 是 QListWidgetItem 类型
            selected_style = item.data(0)  # 获取所选项的文本
            self.style_chosen.emit(self.part_name, selected_style)  # 发送部件选择信号
        else:
            print("Invalid item type:", type(item))

    def set_text(self, text):
        
        self.label.setText(text)
        self.part_name = text

    def set_styles(self, styles, paths):
        self.list_widget.clear()
        self.styles = styles
        for style in self.styles:
            if isinstance(style, dict):
                name = style[name]
                path = paths[name] if paths else "None"
            else:
                name = style
                path = style
            item = QListWidgetItem(name)  # 使用样式名称作为列表项的文本
            if path:
                item.setData(Qt.ItemDataRole.UserRole, path)  # 将对应的路径存储在列表项的数据中
            self.list_widget.addItem(item)
            
    def current_style(self):
        return self.list_widget.currentItem().text() if self.list_widget.currentItem() else None


