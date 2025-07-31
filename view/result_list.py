# view/result_list.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import pyqtSignal, Qt
# from model.similarity import ComparisonResult
from pathlib import Path

class ResultListView(QWidget):
    item_clicked = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["文件 A", "文件 B"])
        # 设置表格为只读
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_double_click)
        # 让列宽自适应内容
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        self._full_results = []  # 存储来自controller的完整结果数据
        self._current_results = [] # 存储当前排序后的结果数据

    def set_data(self, results):
        """从外部接收完整的分析结果"""
        self._full_results = results

    def update_view(self, active_metrics: list):
        """根据激活的指标列表，重新排序和渲染表格"""
        if not self._full_results:
            return

        sort_key = active_metrics[0] if active_metrics else None
        
        if sort_key:
            self._current_results = sorted(self._full_results, 
                                           key=lambda x: x.scores.get(sort_key, 0), 
                                           reverse=True)
        elif not self._current_results:
                 self._current_results = self._full_results

        headers = ["文件 A", "文件 B"] + active_metrics
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setRowCount(len(self._current_results))
        for row, item in enumerate(self._current_results):
            # 填充固定的文件列
            file_a_name = Path(item.file_a).name
            file_b_name = Path(item.file_b).name
            self.table.setItem(row, 0, QTableWidgetItem(file_a_name))
            self.table.setItem(row, 1, QTableWidgetItem(file_b_name))
            
            # 动态填充指标列
            for col_idx, metric_name in enumerate(active_metrics):
                score = item.scores.get(metric_name, 0)
                score_text = f"{score * 100:.2f}%"
                self.table.setItem(row, 2 + col_idx, QTableWidgetItem(score_text))

    def _on_double_click(self, row, column):
        if 0 <= row < len(self._current_results):
            self.item_clicked.emit(self._current_results[row])