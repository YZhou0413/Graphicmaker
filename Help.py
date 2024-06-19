import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser, QStackedWidget
from PyQt6.QtGui import QColor, QFont, QIcon
from PyQt6.QtCore import Qt
import markdown

class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Help")
        self.setWindowIcon(QIcon("Icons\elf.png"))
        self.setFixedSize(1000, 600)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        self.button1 = QPushButton(self)
        self.button1.setText("用前必读")
        self.button1.setCheckable(True)
        self.button1.setChecked(True) 
        self.button1.clicked.connect(lambda: self.switch_page(0)) 

        self.button2 = QPushButton(self)
        self.button2.setText("使用指南")
        self.button2.setCheckable(True)
        self.button2.clicked.connect(lambda: self.switch_page(1)) 

        self.button3 = QPushButton(self)
        self.button3.setText("修复乱码文件名")
        self.button3.setCheckable(True)
        self.button3.clicked.connect(lambda: self.switch_page(2)) 
        button_layout.setSpacing(2)
        button_layout.setContentsMargins(2,2,2,2)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        button_layout.addWidget(self.button3)

        style = """
            QPushButton {
                background-color: #CDC4D7; 
                border-width: 2px; 
                border-radius: 5px; 
                padding: 5px; 
            }
            QPushButton:hover {
                background-color: #dedae3;
            }
            QPushButton:checked {
                background-color: #EEEEEE;
            }
        """

        self.button1.setStyleSheet(style)
        self.button2.setStyleSheet(style)
        self.button3.setStyleSheet(style)

        self.stacked_widget = QStackedWidget(self)
        main_layout.addWidget(self.stacked_widget)
    

        for i in range(3):
            page_widget = QWidget(self)
            page_layout = QVBoxLayout(page_widget)
            page_layout.setContentsMargins(10, 0, 10, 10)
            page_layout.setSpacing(2)
            page_widget.setLayout(page_layout)

            text_browser = QTextBrowser(page_widget)
            text_browser.setOpenExternalLinks(True)
            text_browser.setStyleSheet("""
                QTextBrowser {
                    background-color: #EEEEEE;
                    border-radius: 5px;
                    margin: 0px;
                    padding: 2px;
                }
            """)
            text_browser.setFont(QFont("Source Han Sans SC Medium", 12))

            if i == 0:
                self.load_markdown_file(text_browser, "README.md")
            elif i == 1:
                self.load_markdown_file(text_browser, "Guide.md")
            elif i == 2:
                self.load_markdown_file(text_browser, "FixPic.md")

            page_layout.addWidget(text_browser)
            self.stacked_widget.addWidget(page_widget)

        self.setStyleSheet("background-color: #dedae3;")

    def load_markdown_file(self, browser, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                markdown_text = f.read()
            html_content = markdown.markdown(markdown_text)
            browser.setHtml(html_content)
        except IOError:
            print(f"Error: Could not open or read file {file_path}")

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.button1.setChecked(index == 0)
        self.button2.setChecked(index == 1)
        self.button3.setChecked(index == 2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = HelpWidget()
    mainWin.show()
    sys.exit(app.exec())
