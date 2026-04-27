import sys
import os
import qdarktheme
import qtawesome as qta
from dataclasses import dataclass
import copy
from services.feed_manager import FeedManager
from views.feed_info_editor import FeedInfoEditor
from views.post_editor import RSSPostEditor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QStackedWidget,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QInputDialog,
    QMessageBox,
    QComboBox,
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QPixmap, QFont, QSyntaxHighlighter, QTextCharFormat

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = ""
VERSION_NUMBER = "0.0.0 Alpha"

@dataclass
class PostData:
    id: int = -1
    title: str = "Untitled Post"
    url: str = ""
    description: str = ""
    pubdate: QDateTime = QDateTime.currentDateTime()

class FeedData:
    def __init__(self, title: str = "Untitled Feed", url: str = "", description: str = ""):
        self.title = title
        self.url = url
        self.description = description
        self.posts = []

class PostBtn(QPushButton):
    def __init__(self, post_data: PostData):
        super().__init__()

        self.entry = post_data

        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("padding: 4px; text-align: left;")
            
        self.title_label = QLabel(self.entry.title)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.title_label.setWordWrap(True)

        self.description_label = QLabel(self.entry.description)
        self.description_label.setText(self.entry.description if len(self.entry.description) < 300 else f"{self.entry.description[:300]}...")
        self.description_label.setStyleSheet("font-size: 14px;")
        self.description_label.setWordWrap(True)

        self.pub_date_label = QLabel()
        self.pub_date_label.setText(self.entry.pubdate)

        self.pub_date_label.setStyleSheet("font-size: 12px; color: gray;")
        self.pub_date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.pub_date_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setSpacing(0)

        layout.addWidget(self.title_label)
        layout.addWidget(self.description_label)
        layout.addWidget(self.pub_date_label)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RSS Feed Manager")
        self.resize(640, 480)
        self.setMinimumSize(640, 320)

        self.init_menu_bar()
        self.init_ui()

    def init_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        edit_menu = menu_bar.addMenu("&Edit")
        view_menu = menu_bar.addMenu("&View")
        help_menu = menu_bar.addMenu("&Help")

        # File Menu Actions
        add_local_feed_action = file_menu.addAction("Import RSS Feed...")
        add_local_feed_action.triggered.connect(self.select_local_feed)

        add_feed_from_url_action = file_menu.addAction("Import RSS Feed from URL...")
        add_feed_from_url_action.triggered.connect(self.import_feed_from_url)

        self.export_feed_action = file_menu.addAction("Export Feed...")
        self.export_feed_action.setEnabled(False)
        self.export_feed_action.triggered.connect(self.export_feed)

        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")

        # Edit Menu Actions
        edit_feed_info_action = edit_menu.addAction("Edit Feed Info")
        edit_feed_info_action.triggered.connect(self.switch_to_feed_info_editor)

        # View Menu Actions
        refresh_feeds_action = view_menu.addAction("Refresh Feed View")
        refresh_feeds_action.triggered.connect(self.refresh_feed_view)

        # Help Menu Actions
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.about_dialog)
    
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Feed UI
        main_feed_layout = QVBoxLayout()
        main_layout.addLayout(main_feed_layout)

        controls_layout = QHBoxLayout()
        main_feed_layout.addLayout(controls_layout)

        self.back_to_feed_btn = QPushButton("Back to Feed")
        self.back_to_feed_btn.setIcon(qta.icon("fa6s.arrow-left"))
        self.back_to_feed_btn.setProperty("class", "control-btn")
        self.back_to_feed_btn.setVisible(False)
        self.back_to_feed_btn.clicked.connect(self.switch_to_feed_view)
        controls_layout.addWidget(self.back_to_feed_btn)

        controls_layout.addStretch()

        self.sort_by_combobox = QComboBox()
        self.sort_by_combobox.addItems(["Sort by Date", "Sort by Title"])
        self.sort_by_combobox.setProperty("class", "control-btn")
        self.sort_by_combobox.setFixedWidth(200)
        self.sort_by_combobox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.sort_by_combobox.currentIndexChanged.connect(self.refresh_feed_view)
        controls_layout.addWidget(self.sort_by_combobox)

        self.order_btn = QPushButton("Asc")
        self.order_btn.setCheckable(True)
        self.order_btn.setIcon(qta.icon("mdi.sort-ascending"))
        self.order_btn.setProperty("class", "control-btn")
        self.order_btn.clicked.connect(self.refresh_feed_view)
        controls_layout.addWidget(self.order_btn)

        edit_feed_info_btn = QPushButton("Edit Feed Info")
        edit_feed_info_btn.setIcon(qta.icon("fa6s.pen"))
        edit_feed_info_btn.setProperty("class", "control-btn")
        edit_feed_info_btn.clicked.connect(self.switch_to_feed_info_editor)
        controls_layout.addWidget(edit_feed_info_btn)

        self.delete_post_btn = QPushButton("Delete Post")
        self.delete_post_btn.setIcon(qta.icon("fa6s.trash"))
        self.delete_post_btn.setProperty("class", "control-btn")
        self.delete_post_btn.setVisible(False)
        self.delete_post_btn.clicked.connect(self.delete_current_post)
        controls_layout.addWidget(self.delete_post_btn)

        self.new_post_btn = QPushButton("New Post")
        self.new_post_btn.setIcon(qta.icon("fa6s.plus"))
        self.new_post_btn.setProperty("class", "control-btn")
        self.new_post_btn.setObjectName("new_post_btn")
        self.new_post_btn.setEnabled(False)
        self.new_post_btn.clicked.connect(self.add_new_post)
        controls_layout.addWidget(self.new_post_btn)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.feed_scrollarea = QScrollArea()
        self.feed_widget = QWidget()
        self.feed_widget_layout = QVBoxLayout()

        self.feed_widget.setLayout(self.feed_widget_layout)
        self.feed_scrollarea.setWidget(self.feed_widget)

        self.feed_scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.feed_scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.feed_scrollarea.setWidgetResizable(True)

        self.stacked_widget.addWidget(self.feed_scrollarea)

        # Post Editor UI
        self.post_editor = RSSPostEditor()
        self.post_editor.saved_post.connect(self.save_current_post)
        self.stacked_widget.addWidget(self.post_editor)

        self.stacked_widget.setCurrentWidget(self.feed_scrollarea)

        # Feed info editor UI
        self.feed_info_editor = FeedInfoEditor()
        self.stacked_widget.addWidget(self.feed_info_editor)
    
    def select_local_feed(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select RSS Feed", "", "XML Files (*.xml);;All Files (*)")

        if file:
            if os.path.exists(file):
                self.import_feed(file)
    
    def import_feed_from_url(self):
        url, ok = QInputDialog.getText(self, "Import RSS Feed from URL", "Enter RSS feed URL:", QLineEdit.EchoMode.Normal, "https://")

        if ok and url:
            try:
                self.import_feed(url)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import feed: {str(e)}")
    
    def import_feed(self, feed_data):
        self.clear_layout(self.feed_widget_layout)
        self.new_post_btn.setEnabled(True)
        self.stacked_widget.setCurrentWidget(self.feed_scrollarea)

        try:
            feed_manager.import_feed(feed_data)
            self.feed_info_editor.load_feed_info(feed_manager.feed)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import feed: {str(e)}")
            return
        
        self.refresh_feed_view()
        self.export_feed_action.setEnabled(True)
    
    def export_feed(self):
        if feed_manager.feed is None:
            QMessageBox.warning(self, "No Feed", "There is no feed to export.")
            return

        file, _ = QFileDialog.getSaveFileName(self, "Export RSS Feed", "", "XML Files (*.xml);;All Files (*)")

        if file:
            try:
                feed_manager.export_feed(file)
                QMessageBox.information(self, "Success", "Feed exported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export feed: {str(e)}")
    
    def add_new_post(self):
        feed_manager.add_new_post()
        feed_manager.update_indexes()
        self.refresh_feed_view()
        self.open_post_editor(feed_manager.feed.posts[-1])
    
    def delete_current_post(self):
        if self.post_editor.post_data is None:
            return
        
        current_post_id = self.post_editor.post_data.id
        
        feed_manager.delete_post(current_post_id)
        self.post_editor.post_data = None
        self.switch_to_feed_view()
    
    def save_current_post(self, post_data: PostData):
        feed_manager.update_indexes()
        feed_manager.feed.posts[post_data.id] = post_data
    
    def refresh_feed_view(self):
        if feed_manager.feed is None:
            return

        self.clear_layout(self.feed_widget_layout)
        
        feed = copy.deepcopy(feed_manager.feed)
        ascending = self.order_btn.isChecked()
        sort_by_date = self.sort_by_combobox.currentIndex() == 0

        if sort_by_date:
            feed.posts.sort(key=lambda post: QDateTime.fromString(post.pubdate, Qt.DateFormat.RFC2822Date), reverse=not ascending)
        else:
            feed.posts.sort(key=lambda post: post.title, reverse=not ascending)
        
        if ascending:
            self.order_btn.setIcon(qta.icon("mdi.sort-ascending"))
            self.order_btn.setText("Asc")
        else:
            self.order_btn.setIcon(qta.icon("mdi.sort-descending"))
            self.order_btn.setText("Desc")
        

        for post_data in feed.posts:
            post_btn = PostBtn(post_data)
            post_btn.clicked.connect(lambda checked, pd=post_data: self.open_post_editor(pd))
            post_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
            self.feed_widget_layout.addWidget(post_btn)

        self.feed_widget_layout.addStretch()

    
    def open_post_editor(self, post_data: PostData):
        self.new_post_btn.setVisible(False)
        self.back_to_feed_btn.setVisible(True)
        self.sort_by_combobox.setVisible(False)
        self.order_btn.setVisible(False)
        self.delete_post_btn.setVisible(True)
        self.post_editor.load_post(post_data)
        self.stacked_widget.setCurrentWidget(self.post_editor)

    def switch_to_feed_info_editor(self):
        self.back_to_feed_btn.setVisible(True)
        self.new_post_btn.setVisible(False)
        self.sort_by_combobox.setVisible(False)
        self.order_btn.setVisible(False)
        self.delete_post_btn.setVisible(False)
        self.stacked_widget.setCurrentWidget(self.feed_info_editor)

    def switch_to_feed_view(self):
        self.new_post_btn.setVisible(True)
        self.back_to_feed_btn.setVisible(False)
        self.sort_by_combobox.setVisible(True)
        self.order_btn.setVisible(True)
        self.delete_post_btn.setVisible(False)

        self.post_editor.save_current_post()
        self.refresh_feed_view()

        self.stacked_widget.setCurrentWidget(self.feed_scrollarea)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
    
    def about_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self.tr("About"))
        dlg_layout = QVBoxLayout()
        dlg.setFixedSize(240, 325)

        logoLabel = QLabel(self)
        logoLabel.setFixedSize(170, 170)
        logoLabel.setScaledContents(True)
        
        if os.path.exists(LOGO_PATH):
            logoLabel.setPixmap(QPixmap(LOGO_PATH))

        about_title = QLabel("RSS MGR")
        about_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        about_description = QLabel("A simple PyQt6 RSS editor")
        about_description.setWordWrap(True)
        about_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_label = QLabel(f"Version: {VERSION_NUMBER}\nSilk Project 2026")
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.setContentsMargins(0, 8, 0, 8)
        button_box.accepted.connect(dlg.accept)

        dlg_layout.addWidget(logoLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        dlg_layout.addWidget(about_title)
        dlg_layout.addWidget(about_description)
        dlg_layout.addWidget(about_label)
        dlg_layout.addWidget(button_box, alignment=Qt.AlignmentFlag.AlignCenter)
        dlg.setLayout(dlg_layout)
        
        dlg.exec()

if __name__ == "__main__":
    qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    app.setApplicationName("RSS Feed Manager")
    app.setStyle("Fusion")

    additional_qss = """
    QPushButton.control-btn {
        padding: 8px;
    }
    """
    qdarktheme.setup_theme("dark", custom_colors={"primary": "#C58EDF"}, additional_qss=additional_qss)

    feed_manager = FeedManager()

    window = MainWindow()

    window.show()
    sys.exit(app.exec())