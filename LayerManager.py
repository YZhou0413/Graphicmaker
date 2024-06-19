import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon
from collections import OrderedDict
from collections import defaultdict

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

    def update_checkbox_state(self, text, state):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget.main_text_label.text() == text:
                widget.set_checked(state)

    def uncheck_all_checkbox(self):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            widget.uncheck_box()

class CustomListWidgetItem(QWidget):
    checkbox_state_label = pyqtSignal(str, bool)
    checked_state = pyqtSignal(bool)
    def __init__(self, number, a, main_text, parent=None):
        super().__init__(parent)
        self.number_label = QLabel(str(number))
        self.a_label = QLabel(f"{a}")
        self.main_text_label = QLabel(main_text)
        self.main_text_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.main_text_label.setWordWrap(False)
        self.main_text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.main_text_label.setStyleSheet("""
            QLabel {
                qproperty-alignment: 'AlignVCenter | AlignLeft';
                max-width: 100px;
                white-space: nowrap;
            }
        """)

        self.checkbox = QCheckBox()
        self.checkbox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.checkbox.stateChanged.connect(self.update_color_layers)

        small_font = QFont()
        small_font.setPointSize(7)

        large_font = QFont()
        large_font.setPointSize(9) 

        self.a_label.setFont(small_font)
        self.main_text_label.setFont(large_font)
        
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.VLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        
        
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.a_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.main_text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        

        middle_layout = QVBoxLayout()
        middle_layout.addWidget(self.a_label)
        middle_layout.addWidget(self.main_text_label)
        
        layout = QHBoxLayout()
        layout.addWidget(self.number_label)
        layout.addWidget(self.separator)
        layout.addLayout(middle_layout)
        layout.addStretch()
        layout.addWidget(self.checkbox)
        
        self.setLayout(layout)

    def is_checked(self):
        return self.checkbox.isChecked()

    def set_checked(self, checked):
        self.checkbox.setChecked(checked)

    def uncheck_box(self):
        self.checkbox.setChecked(False)

    def update_color_layers(self):
        self.checkbox_state_label.emit(self.main_text_label.text(), self.checkbox.isChecked())
        self.checked_state.emit(self.checkbox.isChecked())

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
        self.current_colored_styles = defaultdict(lambda: None)
        self.init_ui()

    def init_ui(self):
        self.LM_label = QLabel("Layer Manager")
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
        self.clear_layer_button = QPushButton("Clear all layers")
        self.clear_checked_box = QPushButton("Reset Check")
        self.clear_checked_box.setIcon(QIcon("Icons\\x-square.svg"))
        self.raise_button.setEnabled(False)
        self.lower_button.setEnabled(False)
        self.clear_layer_button.setEnabled(False)
        self.clear_checked_box.setEnabled(False)
        
        self.lower_button.clicked.connect(lambda: self.lower_layer(self.selected_layer_index))
        self.raise_button.clicked.connect(lambda: self.raise_layer(self.selected_layer_index))
        self.clear_layer_button.clicked.connect(lambda: self.clear_layers_template_change(self))
        self.clear_checked_box.clicked.connect(lambda: self.uncheck_all())
        
        layout = QVBoxLayout()
        button_layout = QGridLayout()
        button_layout.addWidget(self.lower_button, 0, 0)
        button_layout.addWidget(self.raise_button, 0, 1)
        button_layout.addWidget(self.clear_layer_button, 1, 0)
        button_layout.addWidget(self.clear_checked_box, 1, 1)
        self.setFixedSize(210, 400)
        layout.addWidget(self.LM_label)
        layout.addWidget(self.layer_list)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def clear_layers_template_change(self, template):
        self.layers.clear()
        self.refresh_layers()
        self.clear_all_requested.emit()
    
    def uncheck_all(self):
        self.layer_list.uncheck_all_checkbox()

    def set_layer_index(self, index):
        self.selected_layer_index = index

    def add_part_to_order(self, part_name):
        if part_name not in self.layers_order:
            self.layers_order.append(part_name)

    def set_selected_styles(self, object_list):
        if not object_list:
            self.layers.clear()
        else: 
            replacing_styles = self.get_difference_between_dicts(self.layers, object_list)
            already_selected_parts = [k.part_name for k in self.layers.values()]
            if list(replacing_styles.keys())[0] in already_selected_parts:
                for replacing_style in replacing_styles.items():
                    self.replace_style(replacing_style)
            else:
                for part_name, style_objs_list in replacing_styles.items():
                    for style_obj in style_objs_list:
                        style_name = style_obj.style_name
                        self.layers[style_name] = style_obj
        self.refresh_layers()

    def get_difference_between_dicts(self, main, incoming):
        sum_diff = {}
        for part_name, style_objs in incoming.items():
            tmp = []
            for obj in style_objs:
                if obj.style_name in list(main.keys()):
                    pass
                else:
                    tmp.append(obj)
                    sum_diff[part_name] = tmp
        return sum_diff

    def replace_style(self, new_style):
        #new_styles = dict = {"key":[obj1,obj2..]}
        n_part_name = new_style[0]
        list_keys = list(self.layers.keys())
        list_for_i = list(self.layers.values())
        index_needed=[]
        for i, item in enumerate(list_for_i):
            if item.part_name == n_part_name:
                index_needed.append(i)          
        style_list = new_style[1]
        if len(style_list) > len(index_needed): 
            for i, style_obj in enumerate(style_list):
                if i < len(index_needed):
                    list_keys[index_needed[i]] = style_obj.style_name
                    list_for_i[index_needed[i]] = style_obj
                else:
                    insert_position = index_needed[-1] + 1
                    list_keys.insert(insert_position, style_obj.style_name)
                    list_for_i.insert(insert_position, style_obj)
        elif len(style_list) < len(index_needed):
            for i, style_obj in enumerate(style_list):
                if style_obj.real != 0:
                    list_keys[index_needed[i]] = style_obj.style_name
                    list_for_i[index_needed[i]] = style_obj
                else:
                    del list_keys[index_needed[i]]
                    del list_for_i[index_needed[i]]
            del list_keys[index_needed[-1]]
            del list_for_i[index_needed[-1]]
        else:
            for i, style_obj in enumerate(style_list):
                if style_obj.real != 0:
                    list_keys[index_needed[i]] = style_obj.style_name
                    list_for_i[index_needed[i]] = style_obj
                else:
                    del list_keys[index_needed[i]]
                    del list_for_i[index_needed[i]]
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
        if current_item is None:
            self.raise_button.setEnabled(False)
            self.lower_button.setEnabled(False)
            self.clear_layer_button.setEnabled(False)
        else:
            self.raise_button.setEnabled(True)
            self.lower_button.setEnabled(True)
            self.clear_layer_button.setEnabled(True)
    
    def update_uncheck_button(self, check_state_bool):
        if check_state_bool == True:
            self.clear_checked_box.setEnabled(True)

    def refresh_layers(self):
        checkbox_states = {}
        for i in range(self.layer_list.count()):
            item = self.layer_list.item(i)
            widget_item = self.layer_list.itemWidget(item)
            if widget_item:
                layer_identifier = widget_item.main_text_label.text() 
                checkbox_states[layer_identifier] = widget_item.is_checked()

        self.layer_list.clear()

        if self.layers:
            for i, (layer_name, layer_data) in enumerate(reversed(list(self.layers.items()))):
                item = QListWidgetItem(self.layer_list)
                widget_item = CustomListWidgetItem(i + 1, layer_data.part_name, layer_data.style_name)
                widget_item.checkbox_state_label.connect(self.handle_color_change_list)
                widget_item.checked_state.connect(self.update_uncheck_button)
                item.setSizeHint(widget_item.sizeHint())
                self.layer_list.setItemWidget(item, widget_item)

            for i in range(self.layer_list.count()):
                item = self.layer_list.item(i)
                widget_item = self.layer_list.itemWidget(item)
                if widget_item:
                    layer_identifier = widget_item.main_text_label.text()
                    checkbox_state = widget_item.checkbox.isChecked()
                    if layer_identifier in checkbox_states:
                        state = checkbox_states[layer_identifier]
                        widget_item.set_checked(state)
                        self.layer_list.update_checkbox_state(widget_item, state)
        self.update_preview_dict.emit(self.layers)
        
    
    def handle_color_change_list(self, layer_name_for_cAdj, checkbox_state):
        style_obj = self.layers[layer_name_for_cAdj]
        part_name = style_obj.part_name
        if checkbox_state == True:
            if self.current_colored_styles[part_name]:
                if style_obj != self.current_colored_styles[part_name]:
                    self.current_colored_styles[part_name] = style_obj
            else:
                self.current_colored_styles[part_name] = style_obj

        else:
            if self.current_colored_styles[part_name]:
                if style_obj == self.current_colored_styles[part_name]:
                    del self.current_colored_styles[part_name]


    def update_color_adjustments(self, hue, saturation, brightness, alpha):
        if self.current_colored_styles:
            for part_name, color_style_obj in self.current_colored_styles.items():
                for key, style_obj in self.layers.items():
                    if key == color_style_obj.style_name:
                        style_obj.set_color_adjustments(hue, saturation, brightness, alpha)
            self.update_preview_dict.emit(self.layers)




    
        


