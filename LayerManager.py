import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QCursor, QFont
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
        self.from_index = self.currentRow()
        event.accept()

    def dropEvent(self, event):
        to_index = self.indexAt(event.position().toPoint()).row() if self.indexAt(event.position().toPoint()).isValid() else -1
        self.itemMoved.emit(self.from_index, to_index)
        event.accept()

class CustomListWidgetItem(QWidget):
    color_text = pyqtSignal(str)
    def __init__(self, number, a, main_text, parent=None):
        super().__init__(parent)
        
        self.number_label = QLabel(str(number))
        self.a_label = QLabel(f"{a}")
        self.main_text_label = QLabel(main_text)
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.update_color_layers)

        small_font = QFont()
        small_font.setPointSize(7)

        large_font = QFont()
        large_font.setPointSize(10) 

        self.a_label.setFont(small_font)
        self.main_text_label.setFont(large_font)
        
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.VLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        
        
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.a_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.main_text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 创建垂直布局，中间的标签
        middle_layout = QVBoxLayout()
        middle_layout.addWidget(self.a_label)
        middle_layout.addWidget(self.main_text_label)
        
        # 创建水平布局，左侧的数字，中间的标签和右侧的复选框
        layout = QHBoxLayout()
        layout.addWidget(self.number_label)
        layout.addWidget(self.separator)
        layout.addLayout(middle_layout)
        layout.addStretch()
        layout.addWidget(self.checkbox)
        
        self.setLayout(layout)

    def update_color_layers(self):
        self.color_text.emit(self.main_text_label.text())

class LayerManager(QWidget):
    clear_all_requested = pyqtSignal()
    update_preview_dict = pyqtSignal(OrderedDict)
    def __init__(self, preview):
        super().__init__()
        self.setWindowTitle('Layer Manager')
        self.preview = preview
        self.layers = OrderedDict()
        self.layers_order = [] # depend on what part is clicked first
        self.selected_layer_index = -1
        self.current_colored_styles = []
        self.init_ui()

    def init_ui(self):
        Titel_label = QLabel("Layer Manager")
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
        self.clear_button = QPushButton("Clear all")
        self.raise_button.setEnabled(False)
        self.lower_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        
        self.lower_button.clicked.connect(lambda: self.lower_layer(self.selected_layer_index))
        self.raise_button.clicked.connect(lambda: self.raise_layer(self.selected_layer_index))
        self.clear_button.clicked.connect(lambda: self.clear_layers_template_change(self))
        
        layout = QVBoxLayout()
        button_layout = QGridLayout()
        button_layout.addWidget(self.lower_button, 0, 0)
        button_layout.addWidget(self.raise_button, 0, 1)
        button_layout.addWidget(self.clear_button, 1, 0, 1, 2)
        self.setFixedSize(220, 400)
        layout.addWidget(Titel_label)
        layout.addWidget(self.layer_list)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def clear_layers_template_change(self, template):
        self.layers.clear()
        self.refresh_layers()
        self.clear_all_requested.emit()

    def set_layer_index(self, index):
        self.selected_layer_index = index

    def add_part_to_order(self, part_name):
        if part_name not in self.layers_order:
            self.layers_order.append(part_name)

    def set_selected_styles(self, new_layers):
        if not new_layers:
            self.layers.clear()
        else: 
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
            to_index = self.layer_list.count() - 1

        item = self.layer_list.takeItem(from_index)
        widget = self.layer_list.itemWidget(item)

        self.layer_list.insertItem(to_index, item)
        self.layer_list.setItemWidget(item, widget)
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
            self.clear_button.setEnabled(False)
        else:
            self.raise_button.setEnabled(True)
            self.lower_button.setEnabled(True)
            self.clear_button.setEnabled(True)

    def refresh_layers(self):
        self.layer_list.clear()
        if self.layers:
            for i, (layer_name, layer_data) in enumerate(reversed(list(self.layers.items()))):
                item = QListWidgetItem(self.layer_list)
                widget_item = CustomListWidgetItem(i + 1, layer_data.part_name, layer_data.style_name)
                widget_item.color_text.connect(self.handle_color_change_list)
                item.setSizeHint(widget_item.sizeHint())
                self.layer_list.setItemWidget(item, widget_item)
                self.update_preview_dict.emit(self.layers)
        else:
            self.preview.clear_preview()
    
    def handle_color_change_list(self, layer_name_for_cAdj):
        if layer_name_for_cAdj:
            if layer_name_for_cAdj in self.current_colored_styles:
                self.current_colored_styles.remove(layer_name_for_cAdj)
            else:
                self.current_colored_styles.append(layer_name_for_cAdj)


    def update_color_adjustments(self, hue, saturation, brightness, alpha):
        if self.current_colored_styles:
            for colored_style in self.current_colored_styles:
                for key, style_obj in self.layers.items():
                    if key == colored_style:
                        style_obj.set_color_adjustments(hue, saturation, brightness, alpha)
            self.refresh_layers()




    
        


