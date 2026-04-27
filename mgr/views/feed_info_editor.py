from PyQt6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
)
from PyQt6.QtCore import Qt

class FeedData:
    def __init__(self, title: str = "Untitled Feed", url: str = "", description: str = ""):
        self.title = title
        self.url = url
        self.description = description
        self.posts = []

class FeedInfoEditor(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.init_ui()

    def init_ui(self):
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.ui_title = QLabel("Edit Feed Info")
        self.ui_title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 14px;")
        self.ui_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addRow(self.ui_title)

        self.feed_title_input = QLineEdit()
        self.layout.addRow("Title:", self.feed_title_input)

        self.feed_url_input = QLineEdit()
        self.layout.addRow("URL:", self.feed_url_input)

        self.feed_description_input = QTextEdit()
        self.layout.addRow("Description:", self.feed_description_input)

    def load_feed_info(self, feed_data: FeedData):
        self.feed_title_input.setText(feed_data.title)
        self.feed_url_input.setText(feed_data.url)
        self.feed_description_input.setPlainText(feed_data.description)