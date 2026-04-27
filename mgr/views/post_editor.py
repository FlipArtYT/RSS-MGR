from services.highlighter import MarkdownHighlighter
from dataclasses import dataclass
from services.feed_manager import PostData
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QTextEdit,
    QLineEdit,
    QDateTimeEdit,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QScrollArea,
    QStackedWidget,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QComboBox,
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal

class RSSPostEditor(QWidget):
    saved_post = pyqtSignal(PostData)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.post_data = None

        self.init_ui()

    def init_ui(self):
        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.post_title = QLineEdit()
        self.post_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addRow(self.post_title)

        self.post_content = QTextEdit()
        self.post_content.setAcceptRichText(True)
        self.markdown_highlighter = MarkdownHighlighter(self.post_content.document())
        self.layout.addRow(self.post_content)

        self.url_input = QLineEdit()
        self.layout.addRow("URL:", self.url_input)

        self.date_time_edit = QDateTimeEdit()
        self.date_time_edit.setCalendarPopup(True)
        self.layout.addRow("Publish Date:", self.date_time_edit)
    
    def load_post(self, post_data: PostData):
        self.post_data = post_data

        self.post_title.setText(post_data.title)
        self.post_content.setPlainText(post_data.description)
        self.date_time_edit.setDateTime(QDateTime.fromString(post_data.pubdate, Qt.DateFormat.RFC2822Date))
        self.url_input.setText(post_data.url)

    def save_current_post(self):
        # Save the edited post data back to the feed manager
        if self.post_data is not None:
            self.post_data.title = self.post_title.text()
            self.post_data.description = self.post_content.toPlainText()
            self.post_data.pubdate = self.date_time_edit.dateTime().toString(Qt.DateFormat.RFC2822Date)
            self.post_data.url = self.url_input.text()
            self.saved_post.emit(self.post_data)