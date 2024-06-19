import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QLineEdit, QHBoxLayout
from PyQt6.QtGui import QColor, QIntValidator, QPainter, QBrush, QPen
from PyQt6.QtCore import Qt, pyqtSignal

class ColorSlider(QSlider):
    def __init__(self, color_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_func = color_func
        self.setFixedHeight(10)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        rect = self.rect()

        painter.fillRect(rect, self.palette().window())

        rect_width = rect.width() / (self.maximum() - self.minimum())

        for i in range(self.minimum(), self.maximum() + 1):
            color = self.color_func(i)
            painter.setPen(QPen(color))
            painter.setBrush(QBrush(color))
            x = int((i - self.minimum()) * rect_width)
            painter.drawRect(x, 0, int(rect_width), rect.height())

        slider_position = int((self.value() - self.minimum()) * rect_width)
        handle_color = self.color_func(self.value())
        handle_radius = 7

        shadow_layers = 5
        shadow_color = QColor(0, 0, 0)
        for i in range(shadow_layers):
            alpha = int(50 * (1 - (i / shadow_layers)))
            shadow_color.setAlpha(alpha)
            painter.setBrush(QBrush(shadow_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(slider_position - handle_radius - i, rect.height() // 2 - handle_radius - i, 2 * (handle_radius + i), 2 * (handle_radius + i))
        painter.setBrush(QBrush(handle_color))
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawEllipse(slider_position - handle_radius, rect.height() // 2 - handle_radius, 2 * handle_radius, 2 * handle_radius)

        painter.end()


class ColorAdjuster(QWidget):
    hsba_changed = pyqtSignal(int, int, int, int)
    bg_color = pyqtSignal(int, int, int, int)
    def __init__(self):
        super().__init__()
        self.allow = False
        layout = QVBoxLayout()
        layout.setSpacing(3)
        self.hue_slider = self.create_slider("Hue", 0, 359, self.hue_color)
        self.brightness_slider = self.create_slider("Brightness", 0, 255, self.brightness_color)
        self.saturation_slider = self.create_slider("Saturation", 0, 255, self.saturation_color)

        self.alpha_label = QLabel("Alpha")
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(100)
        self.alpha_slider.setValue(100)
        self.alpha_slider.valueChanged.connect(self.update_alpha_from_slider)

        self.alpha_edit = QLineEdit()
        self.alpha_edit.setValidator(QIntValidator(0, 100))
        self.alpha_edit.textChanged.connect(self.update_alpha_from_text)
        self.update_alpha_from_slider()

        alpha_layout = QHBoxLayout()
        alpha_layout.addWidget(self.alpha_label)
        alpha_layout.addWidget(self.alpha_slider, 2)
        alpha_layout.addWidget(self.alpha_edit, 1)

        layout.addWidget(self.hue_slider)
        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.saturation_slider)
        layout.addLayout(alpha_layout)

        self.setLayout(layout)
        self.mani_signal_connection(self.allow)
        self.setFixedSize(230, self.sizeHint().height())

        self.hue_slider.findChild(QSlider).valueChanged.connect(self.emit_color_value)
        self.saturation_slider.findChild(QSlider).valueChanged.connect(self.emit_color_value)
        self.brightness_slider.findChild(QSlider).valueChanged.connect(self.emit_color_value)
        self.alpha_slider.valueChanged.connect(self.emit_color_value)

    def create_slider(self, name, min_val, max_val, color_func):
        label = QLabel(name)
        slider = ColorSlider(color_func, Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(min_val)

        setattr(self, name.lower() + '_slider', slider)

        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.addWidget(label)
        container_layout.addWidget(slider)
        container.setLayout(container_layout)

        return container

    def hue_color(self, value):
        return QColor.fromHsl(value, 255, 127)

    def brightness_color(self, value):
        return QColor.fromHsl(self.hue_slider.findChild(QSlider).value(), self.saturation_slider.findChild(QSlider).value(), value)

    def saturation_color(self, value):
        return QColor.fromHsl(self.hue_slider.findChild(QSlider).value(), value, self.brightness_slider.findChild(QSlider).value())

    def update_alpha_from_text(self):
        alpha_text = self.alpha_edit.text()
        if alpha_text.isdigit():
            alpha_value = int(alpha_text)
            if 0 <= alpha_value <= 100:
                self.alpha_slider.setValue(alpha_value)

    def update_alpha_from_slider(self):
        alpha_value = self.alpha_slider.value()
        self.alpha_edit.setText(str(alpha_value))
    
    def mani_signal_connection(self, allow):
        try:
            self.hue_slider.findChild(QSlider).valueChanged.disconnect()
            self.saturation_slider.findChild(QSlider).valueChanged.disconnect()
            self.brightness_slider.findChild(QSlider).valueChanged.disconnect()
            self.alpha_slider.valueChanged.disconnect()
        except TypeError:
            pass 
        if allow == False:
            self.hue_slider.findChild(QSlider).valueChanged.connect(self.emit_color_value)
            self.saturation_slider.findChild(QSlider).valueChanged.connect(self.emit_color_value)
            self.brightness_slider.findChild(QSlider).valueChanged.connect(self.emit_color_value)
            self.alpha_slider.valueChanged.connect(self.emit_color_value)
        else:
            self.hue_slider.findChild(QSlider).valueChanged.connect(self.emit_color_for_bg)
            self.saturation_slider.findChild(QSlider).valueChanged.connect(self.emit_color_for_bg)
            self.brightness_slider.findChild(QSlider).valueChanged.connect(self.emit_color_for_bg)
            self.alpha_slider.valueChanged.connect(self.emit_color_for_bg)


    def emit_color_value(self):
        hue = self.hue_slider.findChild(QSlider).value()
        saturation = self.saturation_slider.findChild(QSlider).value()
        brightness = self.brightness_slider.findChild(QSlider).value()
        alpha = int(self.alpha_slider.value() * 255 / 100)
        self.hsba_changed.emit(hue, saturation, brightness, alpha)
        
    

    def emit_color_for_bg(self):
        hue = self.hue_slider.findChild(QSlider).value()
        saturation = self.saturation_slider.findChild(QSlider).value()
        brightness = self.brightness_slider.findChild(QSlider).value()
        alpha = int(self.alpha_slider.value() * 255 / 100)
        self.bg_color.emit(hue, saturation, brightness, alpha)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ColorAdjuster()
    mainWin.setWindowTitle("Color Adjuster")
    mainWin.show()
    sys.exit(app.exec())