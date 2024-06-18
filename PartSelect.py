from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QListWidget, QListWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt
import random
from collections import defaultdict

class PartSelector(QWidget):
    style_chosen = pyqtSignal(str, str) 
    chosen_styles_to_layer = pyqtSignal(defaultdict)

    def __init__(self, part_name, _styles, parent=None):
        super().__init__(parent)
        self.part_name = part_name
        self.styles = []
        self.block_layout = QVBoxLayout()
        self.setup_ui()
        self.last_clicked_item = None

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
        if isinstance(item, QListWidgetItem):
            if item != self.last_clicked_item:
                selected_style = item.text()
                self.style_chosen.emit(self.part_name, selected_style)
                self.last_clicked_item = item
            else:
                pass
        else:
            print("Invalid item type:", type(item))
    
    def set_item_data(self, item, object_list):
        if list(object_list.keys())[0] == self.part_name:
            if isinstance(item, QListWidgetItem):
                if item == list(object_list.values())[0].style_name:
                    item.setData(Qt.ItemDataRole.UserRole, list(object_list.values()))

            
    def clear_item_select(self):
        if self.list_widget.selectedItems():
            self.list_widget.clearSelection()
            self.list_widget.setCurrentItem(None)

    def set_text(self, text):
        self.label.setText(text)
        self.part_name = text

    def set_styles(self, styles):
        self.list_widget.clear()
        self.styles = styles
        for style in self.styles:
            item = QListWidgetItem(style)
            self.list_widget.addItem(item)
            
    def current_style(self):
        current_item = self.list_widget.currentItem()
        if current_item and current_item.text() is not None:
            return current_item.text()
        else:
            return
    
    def random_select(self):
        if self.list_widget.count() > 0:
            if self.list_widget.selectedItems():
                self.list_widget.clearSelection()
            random_item = self.list_widget.item(random.randint(1, self.list_widget.count() - 1))
            random_data = random_item.data(0)
            self.list_widget.setCurrentItem(random_item)
            self.list_widget.setFocus()
            if random_item != self.last_clicked_item:
                self.style_chosen.emit(self.part_name, random_data)
                self.last_clicked_item = random_item
            else:
                pass
    


