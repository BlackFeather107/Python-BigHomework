# view/detail_view.py

from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QHBoxLayout
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QColor
from model.similarity import ComparisonResult

class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, segments, offset):
        super().__init__(parent.document())
        self.segments = segments
        self.offset = offset
        self.format = QTextCharFormat()
        self.format.setBackground(QColor('#FFFF00'))  # 黄色标记

    def highlightBlock(self, text):
        block_start = self.currentBlock().position()
        block_end = block_start + len(text)
        for (a_start, a_end, b_start, b_end) in self.segments:
            start = a_start if self.offset == 'a' else b_start
            end = a_end if self.offset == 'a' else b_end
            # 判断当前文本块是否与高亮片段有重叠
            if block_end > start and block_start < end:
                hl_start = max(start - block_start, 0)
                hl_length = min(end, block_end) - max(start, block_start)
                self.setFormat(hl_start, hl_length, self.format)

class DetailView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        # 左侧代码展示
        self.editor_a = QPlainTextEdit(self)
        self.editor_a.setReadOnly(True)
        # 右侧代码展示
        self.editor_b = QPlainTextEdit(self)
        self.editor_b.setReadOnly(True)
        layout.addWidget(self.editor_a)
        layout.addWidget(self.editor_b)

    def show(self, comparison: ComparisonResult):
        """根据 ComparisonResult 更新左右编辑器，并高亮相似代码段。"""
        # 读取并设置文本
        from pathlib import Path
        code_a = Path(comparison.file_a).read_text(encoding='utf-8')
        code_b = Path(comparison.file_b).read_text(encoding='utf-8')
        self.editor_a.setPlainText(code_a)
        self.editor_b.setPlainText(code_b)

        # 清除旧高亮器
        for hl in getattr(self, '_highlighters', []):
            hl.deleteLater()
        self._highlighters = []
        # 创建新高亮器
        hl_a = CodeHighlighter(self.editor_a, comparison.segments, offset='a')
        hl_b = CodeHighlighter(self.editor_b, comparison.segments, offset='b')
        self._highlighters.extend([hl_a, hl_b])