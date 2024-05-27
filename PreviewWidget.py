from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import Qt
import os
class PreviewGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.edit = False
        
    def init_ui(self):
        self.setFixedSize(250, 250)
        self.setWindowTitle('Preview')

        # 创建场景
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # 创建灰色背景
        self.set_gray_background()
        self.image_items = []

    def set_gray_background(self):
        # 创建灰色背景图片
        gray_image = QPixmap(self.size())
        gray_image.fill(QColor('lightgray'))

        # 创建背景图像项并添加到场景
        self.background_item = QGraphicsPixmapItem(gray_image)
        self.background_item.setZValue(-1)  # 将背景图像放置在所有图像项的下方
        self.scene.addItem(self.background_item)

    def update_preview(self, image_paths):
        # Remove existing image items
        for item in self.image_items:
            self.scene.removeItem(item)
        self.image_items.clear()

        # Add new image items
        for image_path in image_paths:
            image_path_str = os.fsdecode(image_path)
            pixmap = QPixmap(image_path_str)
            if not pixmap.isNull():
                pixmap_item = QGraphicsPixmapItem(pixmap)
                self.scene.addItem(pixmap_item)
                self.image_items.append(pixmap_item)
            else:
                print(f'Error: Invalid image at {image_path}')
        
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.show()