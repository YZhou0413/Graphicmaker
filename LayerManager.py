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
        self.layers_order = [] # depend on what part is clicked first
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
    def add_part_to_order(self, part_name):
        if part_name not in self.layers_order:
            self.layers_order.append(part_name)

    def set_selected_styles(self, new_layers):
        replacing_styles = self.get_difference_between_dicts(self.layers, new_layers)
        already_selected_parts = [k.part_name for k in self.layers.values()]
        if list(replacing_styles.keys())[0] in already_selected_parts:
            for replacing_style in replacing_styles.items():
                self.replace_style(replacing_style)
        else:
            for part_name, styles_for_part in replacing_styles.items():
                for style_dict in styles_for_part:
                    [(style_name, style_path)] = style_dict.items()
                    new_style = Style(style_path, part_name, style_name)
                    self.layers[style_name] = new_style
        self.refresh_layers()

    def get_difference_between_dicts(self, main, incoming):
        sum_diff = {}
        for part_name, incoming_styles in incoming.items():
            tmp = []
            for incoming_style in incoming_styles:
                if list(incoming_style.keys())[0] in list(main.keys()):
                    pass
                else:
                    tmp.append(incoming_style)
                    sum_diff[part_name] = tmp
        return sum_diff

    def replace_style(self, new_style):
        n_part_name = new_style[0]
        list_keys = list(self.layers.keys())
        list_for_i = list(self.layers.values())
        index_needed=[]
        for i, item in enumerate(list_for_i):
            if item.part_name == n_part_name:
                index_needed.append(i)          
        style_list = new_style[1]

        if len(style_list) > len(index_needed): 
            for i, style_dict in enumerate(style_list):
                if i < len(index_needed):
                    [(name, path)] = style_dict.items()
                    list_keys[index_needed[i]] = name
                    list_for_i[index_needed[i]] = Style(path, n_part_name, name)
                else:
                    insert_position = index_needed[-1] + 1
                    [(name, path)] = style_dict.items()
                    list_keys.insert(insert_position, name)
                    list_for_i.insert(insert_position, Style(path, n_part_name, name))
        elif len(style_list) < len(index_needed):
            for i, style_dict in enumerate(style_list):
                [(name, path)] = style_dict.items()
                list_keys[index_needed[i]] = name
                list_for_i[index_needed[i]] = Style(path, n_part_name, name)
            del list_keys[len(style_list):]
            del list_for_i[len(style_list):]
        else:
            for i, style_dict in enumerate(style_list):
                [(name, path)] = style_dict.items()
                list_keys[index_needed[i]] = name
                list_for_i[index_needed[i]] = Style(path, n_part_name, name)
        self.layers = OrderedDict(zip(list_keys, list_for_i))

                


    def move_item_in_list(self, from_index, to_index):
        if from_index == to_index \
                or from_index < 0 \
                or to_index < 0 \
                or from_index >= self.layer_list.count():
            return
        elif to_index >= self.layer_list.count():
            to_index = int(self.layer_list.count() - 1)

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

        keys[dict_from_index], keys[dict_to_index] = keys[dict_to_index], keys[dict_from_index]
        values[dict_from_index], values[dict_to_index] = values[dict_to_index], values[dict_from_index]

        self.layers = OrderedDict(zip(keys, values))

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



    
        


