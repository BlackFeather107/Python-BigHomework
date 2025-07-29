# view/result_list.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt
from model.similarity import ComparisonResult
from pathlib import Path

class ResultListView(QWidget):
    # 当点击某行时发出 ComparisonResult 对象
    item_clicked = pyqtSignal(ComparisonResult)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 3, self)
        self.table.setHorizontalHeaderLabels(["文件 A", "文件 B", "重复率"])
        # 设置表格为只读
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)

        self.results = []  # 存储当前展示的 ComparisonResult 列表

    def display(self, results):
        """接受 ComparisonResult 列表并按降序展示，仅显示文件名且只读。"""
        self.results = results
        self.table.setRowCount(len(results))
        for row, item in enumerate(results):
            name_a = Path(item.file_a).name
            name_b = Path(item.file_b).name
            name_item_a = QTableWidgetItem(name_a)
            name_item_b = QTableWidgetItem(name_b)
            rate_text = f"{item.score * 100:.2f}%"
            rate_item = QTableWidgetItem(rate_text)
            # 设置只读标志
            for it in (name_item_a, name_item_b, rate_item):
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item_a)
            self.table.setItem(row, 1, name_item_b)
            self.table.setItem(row, 2, rate_item)
        self.table.resizeColumnsToContents()

    def _on_double_click(self, row, column):
        if 0 <= row < len(self.results):
            self.item_clicked.emit(self.results[row])