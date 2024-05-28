import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtCore import pyqtSignal, QEvent
from PyQt6.QtGui import QCursor
from collections import OrderedDict, deque
from PreviewWidget import PreviewGraphicsView
from Style import Style

class MyListWidget(QListWidget):
    itemMoved = pyqtSignal(int, int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)  
        self.from_Index = -1

    def dragMoveEvent(self, event):
        # 记录开始拖动的项的索引
        self.from_index = self.currentRow()
        event.accept()

    def dropEvent(self, event):
        to_index = self.indexAt(event.position().toPoint()).row() if self.indexAt(event.position().toPoint()).isValid() else -1
        self.itemMoved.emit(self.from_index, to_index)
        event.accept()


class LayerManager(QWidget):
    def __init__(self, preview):
        super().__init__()
        self.setWindowTitle('Layer Manager')
        self.preview = preview
        self.layers = OrderedDict()
        self.user_defined_order = OrderedDict()
        self.selected_layer_index = -1
        self.init_ui()

    def init_ui(self):
        self.layer_list = MyListWidget()
        self.layer_list.setStyleSheet("""
            QListWidget::item {
                height: 30px;
                border: 1px solid #eeeeee; 
                margin: 2px; 
                background: #f3f6f4;
            }
            QListWidget::item:selected {
                background: #91A3B0; 
            }
        """)    
        self.layer_list.currentRowChanged.connect(self.set_layer_index)
        self.layer_list.itemMoved.connect(self.handle_item_moved) 
        self.layer_list.currentItemChanged.connect(self.update_buttons_state) 

        self.lower_button = QPushButton("Lower Layer")
        self.raise_button = QPushButton("Raise Layer")
        self.raise_button.setEnabled(False)
        self.lower_button.setEnabled(False)
        
        self.lower_button.clicked.connect(lambda: self.lower_layer(self.selected_layer_index))
        self.raise_button.clicked.connect(lambda: self.raise_layer(self.selected_layer_index))
        
        layout = QVBoxLayout()
        layout.addWidget(self.layer_list)
        layout.addWidget(self.lower_button)
        layout.addWidget(self.raise_button)
        self.setLayout(layout)

    def set_layer_index(self, index):
        self.selected_layer_index = index

    def set_selected_styles(self, layers):
        sorted_layers = OrderedDict()
        for part_name, styles_for_part in layers.items():
            for style_dict in styles_for_part:
                [(style_name, style_path)] = style_dict.items()
                new_style = Style(style_path, part_name, style_name)
                sorted_layers[style_name] = new_style
        self.layers = sorted_layers
        self.refresh_layers()

    def move_item_in_list(self, from_index, to_index):
        if from_index == to_index \
                or from_index < 0 \
                or to_index < 0 \
                or from_index >= self.layer_list.count() \
                or to_index >= self.layer_list.count():
            return

        item = self.layer_list.takeItem(from_index)
        self.layer_list.insertItem(to_index, item)
        self.layer_list.setCurrentRow(to_index)

        self.move_item_in_dict(from_index, to_index)
        self.refresh_layers()

    def move_item_in_dict(self, from_index, to_index):
        keys = list(self.layers.keys())
        values = list(self.layers.values())
        if to_index < 0 or to_index >= len(keys):
            return

        dict_from_index = len(keys) - 1 - from_index
        dict_to_index = len(keys) - 1 - to_index

        # 交换键和值
        keys[dict_from_index], keys[dict_to_index] = keys[dict_to_index], keys[dict_from_index]
        values[dict_from_index], values[dict_to_index] = values[dict_to_index], values[dict_from_index]

        self.layers = OrderedDict(zip(keys, values))
        self.user_defined_order = OrderedDict(zip(keys, range(len(keys))))

        self.refresh_layers()
        self.layer_list.setCurrentRow(to_index)

    def lower_layer(self, selected_layer_index):
        to_index = selected_layer_index + 1
        self.move_item_in_dict(selected_layer_index, to_index)

    def raise_layer(self, selected_layer_index):
        to_index = selected_layer_index - 1
        self.move_item_in_dict(selected_layer_index, to_index)

    def handle_item_moved(self, from_index, to_index):
        self.move_item_in_list(from_index, to_index)

    def update_buttons_state(self, current_item):
        # 根据当前项的情况来设置按钮状态
        if current_item is None:
            self.raise_button.setEnabled(False)
            self.lower_button.setEnabled(False)
        else:
            self.raise_button.setEnabled(True)
            self.lower_button.setEnabled(True)

    def refresh_layers(self):
        self.layer_list.clear()
        image_paths = deque()
        for layer_name in reversed(list(self.layers.keys())):
            self.layer_list.addItem(layer_name)
            image_paths.appendleft(self.layers[layer_name].path)
            self.preview.update_preview(image_paths)
            self.show()



    
        


