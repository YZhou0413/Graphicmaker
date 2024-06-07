from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt6.QtGui import QColor, QPixmap, QImage
from PyQt6.QtCore import Qt, QByteArray
import os
import cv2
import numpy as np

class PreviewGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.edit = False
        
    def init_ui(self):
        self.setFixedSize(220, 220)
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
    
    def clear_preview(self):
        for item in self.image_items:
            self.scene.removeItem(item)
        self.image_items.clear()

    def apply_color_adjustments(self, cv_image, hue, saturation, brightness, alpha):
        # Convert BGR to RGB for correct color adjustment
        if cv_image.shape[2] == 4:
            rgb_image = cv2.cvtColor(cv_image[:, :, :3], cv2.COLOR_BGRA2RGB).astype(np.float32)
        else:
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB).astype(np.float32)
        
        # Convert to HSV for color adjustments
        hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV).astype(np.float32)

        # Apply adjustments
        hsv_image[..., 0] = hue % 180  # Hue adjustment
        hsv_image[..., 1] = np.clip(hsv_image[..., 1] + saturation, 0, 255)  # Saturation adjustment
        hsv_image[..., 2] = np.clip(hsv_image[..., 2] + brightness, 0, 255)  # Brightness adjustment

        
        # Convert back to RGB
        adjusted_rgb_image = cv2.cvtColor(hsv_image.astype(np.uint8), cv2.COLOR_HSV2RGB)

        # If original image has alpha channel, merge it back
        if cv_image.shape[2] == 4:
            alpha_channel = np.clip(cv_image[:, :, 3] * (alpha / 255.0), 0, 255).astype(np.uint8)
            adjusted_image = cv2.merge((adjusted_rgb_image, alpha_channel))
        else:
            adjusted_image = adjusted_rgb_image

        return adjusted_image



    def update_preview(self, layers_dict):
        # Remove existing image items
        for item in self.image_items:
            self.scene.removeItem(item)
        self.image_items.clear()

        for (layer_name, item_style_obj) in layers_dict.items():
            image_path_str = os.fsdecode(item_style_obj.path)
            cv_image = cv2.imread(image_path_str, cv2.IMREAD_UNCHANGED)
            if cv_image is not None:
                if item_style_obj.hue is not None:
                    cv_image = self.apply_color_adjustments(cv_image, item_style_obj.hue, item_style_obj.saturation, item_style_obj.brightness, item_style_obj.alpha)

                # Convert the OpenCV image to QPixmap
                _, buffer = cv2.imencode('.png', cv_image)
                image_data = buffer.tobytes()
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                pixmap_item = QGraphicsPixmapItem(pixmap)
                self.scene.addItem(pixmap_item)
                self.image_items.append(pixmap_item)

        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)




