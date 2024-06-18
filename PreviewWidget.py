from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QWidget, QVBoxLayout, QGridLayout, QPushButton, QApplication, QFileDialog
from PyQt6.QtGui import QColor, QPixmap, QImage, QPainter, QIcon, QTransform
from PyQt6.QtCore import Qt, QRectF, QSize, QRect
import os
import cv2
import numpy as np

class PreviewGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.edit = False
        self.flipped = False

    def init_ui(self):
        self.setFixedSize(192, 192)
        self.setWindowTitle('Preview')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scene_ = QGraphicsScene(self)
        self.setScene(self.scene_)

        self.set_gray_background()
        self.image_items = []

    def set_gray_background(self):
        gray_image = QPixmap(self.size())
        gray_image.fill(QColor('lightgray'))

        self.background_item = QGraphicsPixmapItem(gray_image)
        self.background_item.setZValue(-1) 
        self.scene_.addItem(self.background_item)

    def change_bg_color(self, hue, sat, bri, alpha):
        if self.background_item: 
            self.scene_.removeItem(self.background_item)
        color = QColor.fromHsl(hue, sat, bri)
        color.setAlpha(alpha)
        bg_color_i = QPixmap(self.size())
        bg_color_i.fill(color)

        self.background_item = QGraphicsPixmapItem(bg_color_i)
        self.background_item.setZValue(-1) 
        self.scene_.addItem(self.background_item)

    def bg_pic(self):
        if self.background_item:
            self.scene_.removeItem(self.background_item)
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if fileName:
            image = QImage(fileName)
            if not image.isNull():
                if image.width() > image.height():
                    crop_rect = QRect((image.width() - image.height()) // 2, 0, image.height(), image.height())
                else:
                    crop_rect = QRect(0, (image.height() - image.width()) // 2, image.width(), image.width())
                cropped_image = image.copy(crop_rect)
                scaled_image = cropped_image.scaled(QSize(192, 192), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                pixmap_con = QPixmap.fromImage(scaled_image)

            self.background_item = QGraphicsPixmapItem(pixmap_con)
            self.background_item.setZValue(-1) 
            self.scene_.addItem(self.background_item)

    def clear_preview(self):
        for item in self.image_items:
            self.scene_.removeItem(item)
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
            self.scene_.removeItem(item)
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
                self.scene_.addItem(pixmap_item)
                self.image_items.append(pixmap_item)

        self.fitInView(self.scene_.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def flip_view(self):
        self.flipped = not self.flipped
        transform = QTransform().scale(-1, 1) if self.flipped else QTransform()
        self.setTransform(transform)

    
    def save_image_png_bg(self, include_bg, rect=QRectF(0, 0, 192, 192)):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            image = QImage(rect.width(), rect.height(), QImage.Format.Format_ARGB32)
            image.fill(0)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            all_items = self.scene_.items()
            if not include_bg:
                for item in all_items:
                    if item.zValue() == -1:
                        item.setVisible(False)

            self.scene_.render(painter, QRectF(image.rect()), rect)
            painter.end()
            if self.flipped == False:
                image.save(file_path)
            else:
                flipped_image = image.mirrored(True, False)
                flipped_image.save(file_path)    


            if not include_bg:
                for item in all_items:
                    if item.zValue() == -1:
                        item.setVisible(True)       
            

class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.pre_view = PreviewGraphicsView()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        b_flip = QPushButton("horizontal flip")
        b_flip.clicked.connect(self.pre_view.flip_view)
        flip_icon = QIcon("Icons\\symmetry-vertical.svg")
        b_flip.setIcon(flip_icon)

        layout.addWidget(self.pre_view)
        layout.addWidget(b_flip)
        self.setLayout(layout)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = PreviewWidget()
    MainWindow.show()
    sys.exit(app.exec())
    


        




