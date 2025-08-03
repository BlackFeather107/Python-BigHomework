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
        # 获取当前行的行号（1-based）
        current_line_num = self.currentBlock().blockNumber() + 1

        for segment in self.segments:
            # 根据当前是文件A还是文件B，选择对应的坐标
            start_pos, end_pos = (segment[0], segment[1]) if self.is_file_a else (segment[2], segment[3])
            
            start_line, start_col = start_pos
            end_line, end_col = end_pos

            # 检查当前行是否在需要高亮的范围之内
            if start_line <= current_line_num <= end_line:
                # 计算在当前行内高亮的起始列和结束列
                highlight_start_col = start_col if current_line_num == start_line else 0
                highlight_end_col = end_col if current_line_num == end_line else len(text)
                
                # 应用高亮
                length = highlight_end_col - highlight_start_col
                if length > 0:
                    self.setFormat(highlight_start_col, length, self.format)

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