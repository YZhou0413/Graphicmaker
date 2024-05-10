from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QListWidget, QListWidgetItem
from PyQt6.QtGui import QColor, QPixmap

class PreviewLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(300, 200)
        self.set_gray_background()
        self.setWindowTitle('Preview')

    def set_gray_background(self):
        # 创建灰色背景图片
        gray_image = QPixmap(self.size())
        gray_image.fill(QColor('lightgray'))

        # 将灰色背景图片设置为预览标签的背景
        self.setPixmap(gray_image)

    def update_preview(self, image_path):
        pixmap = QPixmap(image_path) 
        self.setPixmap(pixmap)
        self.show()