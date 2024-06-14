from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QWidget, QVBoxLayout, QGridLayout, QPushButton, QApplication
from PyQt6.QtGui import QColor, QPixmap, QImage, QPainter, QIcon
from PyQt6.QtCore import Qt, QByteArray, QRectF
import os
import cv2
import numpy as np

class PreviewGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.edit = False
        
    def init_ui(self):
        self.setFixedSize(192, 192)
        self.setWindowTitle('Preview')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.set_gray_background()
        self.image_items = []

    def set_gray_background(self):
        gray_image = QPixmap(self.size())
        gray_image.fill(QColor('lightgray'))

        self.background_item = QGraphicsPixmapItem(gray_image)
        self.background_item.setZValue(-1) 
        self.scene.addItem(self.background_item)

    def change_bg_color(self, hue, sat, bri, alpha):
        if self.background_item: 
            self.scene.removeItem(self.background_item)
        color = QColor.fromHsl(hue, sat, bri)
        color.setAlpha(alpha)
        bg_color_i = QPixmap(self.size())
        bg_color_i.fill(color)

        self.background_item = QGraphicsPixmapItem(bg_color_i)
        self.background_item.setZValue(-1) 
        self.scene.addItem(self.background_item)

    
    def clear_preview(self):
        for item in self.image_items:
            self.scene.removeItem(item)
        self.image_items.clear()

    def apply_color_adjustments(self, cv_image, hue, saturation, brightness, alpha):
        if cv_image.shape[2] == 4:
            rgb_image = cv2.cvtColor(cv_image[:, :, :3], cv2.COLOR_BGRA2RGB).astype(np.float32)
        else:
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB).astype(np.float32)
        
        hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV).astype(np.float32)

        hsv_image[..., 0] = hue // 2
        hsv_image[..., 1] = np.clip(hsv_image[..., 1] + saturation, 0, 255) 
        hsv_image[..., 2] = np.clip(hsv_image[..., 2] + (brightness - 125), 0, 255) 

        adjusted_rgb_image = cv2.cvtColor(hsv_image.astype(np.uint8), cv2.COLOR_HSV2BGR)

        if cv_image.shape[2] == 4:
            alpha_channel = np.clip(cv_image[:, :, 3] * (alpha / 255.0), 0, 255).astype(np.uint8)
            adjusted_image = cv2.merge((adjusted_rgb_image, alpha_channel))
        else:
            adjusted_image = adjusted_rgb_image

        return adjusted_image

    def update_preview(self, layers_dict):
        for item in self.image_items:
            self.scene.removeItem(item)
        self.image_items.clear()

        for (layer_name, item_style_obj) in layers_dict.items():
            image_path_str = os.fsdecode(item_style_obj.path)
            cv_image = cv2.imread(image_path_str, cv2.IMREAD_UNCHANGED)
            if cv_image is not None:
                if item_style_obj.hue is not None:
                    cv_image = self.apply_color_adjustments(cv_image, item_style_obj.hue, item_style_obj.saturation, item_style_obj.brightness, item_style_obj.alpha)

                _, buffer = cv2.imencode('.png', cv_image)
                image_data = buffer.tobytes()
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                pixmap_item = QGraphicsPixmapItem(pixmap)
                self.scene.addItem(pixmap_item)
                self.image_items.append(pixmap_item)

        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def save_image_png_bg(self, filename, include_bg=False, rect=QRectF(0, 0, 192, 192)):
        scene = self.scene()
        image = QImage(rect.width(), rect.height(), QImage.Format.Format_ARGB32)
        image.fill(0)
        
        painter = QPainter(image)
        
        all_items = scene.items()
        if not include_bg:
            for item in all_items:
                if item.zValue() == -1:
                    item.setVisible(False)

        scene.render(painter, QRectF(image.rect()), rect)

        painter.end()
        
        if not include_bg:
            for item in all_items:
                if item.zValue() == -1:
                    item.setVisible(True)
        
        image.save(filename)

class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.pre_view = PreviewGraphicsView()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        button_layout = QGridLayout()
        b_90_left = QPushButton()
        b_90_left.setToolTip("90° left")
        b_90_right = QPushButton()
        b_90_right.setToolTip("90° right")
        b_flip = QPushButton()
        b_flip.setToolTip("horiziontal flip")
        left_icon = QIcon("Icons\\arrow-90deg-left.svg")
        right_icon = QIcon("Icons\\arrow-90deg-right.svg")
        flip_icon = QIcon("Icons\\symmetry-vertical.svg")
        b_90_left.setIcon(left_icon)
        b_90_right.setIcon(right_icon)
        b_flip.setIcon(flip_icon)
        button_layout.addWidget(b_90_left, 0, 0)
        button_layout.addWidget(b_90_right, 0, 1)
        button_layout.addWidget(b_flip, 0, 2)

        layout.addWidget(self.pre_view)
        layout.addLayout(button_layout)
        self.setLayout(layout)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = PreviewWidget()
    MainWindow.show()
    sys.exit(app.exec())
    


        




