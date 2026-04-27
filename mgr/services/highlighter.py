from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat
import re

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Header formats
        self.header_formats = []
        for i in range(1, 3):
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Bold)
            fmt.setFontPointSize(20 - (i * 3))  # Decrease font size for higher header levels
            self.header_formats.append(fmt)
        
        # Bold format
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Weight.Bold)

        # Italic format
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)

        # Link format
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(Qt.GlobalColor.cyan)
        self.link_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)

    def highlightBlock(self, text):
        # Highlight headers
        for i in range(1, 3):
            pattern = re.compile(r'^(#{' + str(i) + r'})\s+(.*)')
            match = pattern.match(text)
            if match:
                self.setFormat(0, len(text), self.header_formats[i-1])
                return
        
        # Highlight bold text
        for match in re.finditer(r'\*\*(.*?)\*\*', text):
            start, end = match.span()
            self.setFormat(start, end - start, self.bold_format)

        # Highlight italic text
        for match in re.finditer(r'\*(.*?)\*', text):
            start, end = match.span()
            self.setFormat(start, end - start, self.italic_format)

        # Highlight links
        for match in re.finditer(r'\[(.*?)\]\((.*?)\)', text):
            start, end = match.span()
            self.setFormat(start, end - start, self.link_format)