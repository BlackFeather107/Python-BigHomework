# view/detail_view.py

from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QHBoxLayout
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QColor
from model.similarity import ComparisonResult
from pathlib import Path

class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, segments, is_file_a: bool):
        super().__init__(parent.document())
        self.segments = segments
        self.is_file_a = is_file_a
        self.format = QTextCharFormat()
        self.format.setBackground(QColor('#FFFF99'))  # 换了个柔和的黄色

    def highlightBlock(self, text: str):
        """
        在给定的文本块（一行代码）上应用高亮。
        """
        # block_start 是当前行在整个文档中的起始字符位置
        block_start = self.currentBlock().position()
        block_end = block_start + len(text)

        for (a_start, a_end, b_start, b_end) in self.segments:
            # 根据当前是文件A还是文件B，选择对应的坐标
            start_char = a_start if self.is_file_a else b_start
            end_char = a_end if self.is_file_a else b_end

            # 检查当前行与高亮区域是否有交集
            # (max(s1, s2) < min(e1, e2))
            if max(block_start, start_char) < min(block_end, end_char):
                # 计算在当前行内需要高亮的起始位置和长度
                highlight_start_in_block = max(0, start_char - block_start)
                highlight_end_in_block = min(len(text), end_char - block_start)
                highlight_length = highlight_end_in_block - highlight_start_in_block
                
                if highlight_length > 0:
                    self.setFormat(highlight_start_in_block, highlight_length, self.format)

class DetailView(QWidget):
    def __init__(self):
        super().__init__()
        # 代码展示
        layout = QHBoxLayout(self)
        self.editor_a = QPlainTextEdit(self)
        self.editor_a.setReadOnly(True)
        self.editor_b = QPlainTextEdit(self)
        self.editor_b.setReadOnly(True)
        layout.addWidget(self.editor_a)
        layout.addWidget(self.editor_b)
        self._highlighters = []

    def show(self, comparison: ComparisonResult):
        """根据 ComparisonResult 更新左右编辑器，并高亮相似代码段。"""
        # 读取并设置文本
        try:
            code_a = Path(comparison.file_a).read_text(encoding='utf-8')
            code_b = Path(comparison.file_b).read_text(encoding='utf-8')
        except Exception as e:
            code_a = f"无法读取文件: {comparison.file_a}\n错误: {e}"
            code_b = f"无法读取文件: {comparison.file_b}\n错误: {e}"
        self.editor_a.setPlainText(code_a)
        self.editor_b.setPlainText(code_b)

        # 清除旧高亮器
        for hl in self._highlighters:
            hl.setDocument(None) # 解除与文档的关联
        self._highlighters.clear()

        # 创建并应用新高亮器
        hl_a = CodeHighlighter(self.editor_a, comparison.segments, is_file_a=True)
        hl_b = CodeHighlighter(self.editor_b, comparison.segments, is_file_a=False)
        self._highlighters.extend([hl_a, hl_b])