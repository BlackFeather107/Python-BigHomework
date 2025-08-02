# view/result_list.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QContextMenuEvent
from pathlib import Path

class ResultListView(QWidget):
    item_clicked = pyqtSignal(object)
    plagiarism_marked = pyqtSignal(str, str, bool, str)  # 文件A, 文件B, 是否抄袭, 备注

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
        # 启用右键菜单
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
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

        headers = ["文件 A", "文件 B"] + active_metrics + ["抄袭状态"]
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
            
            # 填充抄袭状态列
            plagiarism_status = "已标记" if item.is_plagiarism else "未标记"
            status_item = QTableWidgetItem(plagiarism_status)
            if item.is_plagiarism:
                status_item.setBackground(Qt.red)
                status_item.setForeground(Qt.white)
            self.table.setItem(row, 2 + len(active_metrics), status_item)

    def _on_double_click(self, row, column):
        if 0 <= row < len(self._current_results):
            self.item_clicked.emit(self._current_results[row])

    def _show_context_menu(self, position):
        """显示右键菜单"""
        row = self.table.rowAt(position.y())
        if row < 0 or row >= len(self._current_results):
            return
        
        result = self._current_results[row]
        menu = QMenu(self)
        
        # 标记抄袭菜单项
        if result.is_plagiarism:
            mark_action = QAction("取消抄袭标记", self)
            mark_action.triggered.connect(lambda: self._mark_plagiarism(result, False))
        else:
            mark_action = QAction("标记为抄袭", self)
            mark_action.triggered.connect(lambda: self._mark_plagiarism(result, True))
        
        menu.addAction(mark_action)
        
        # 编辑备注菜单项
        edit_notes_action = QAction("编辑备注", self)
        edit_notes_action.triggered.connect(lambda: self._edit_notes(result))
        menu.addAction(edit_notes_action)
        
        # 显示备注菜单项
        if result.plagiarism_notes:
            show_notes_action = QAction("查看备注", self)
            show_notes_action.triggered.connect(lambda: self._show_notes(result))
            menu.addAction(show_notes_action)
        
        menu.exec_(self.table.mapToGlobal(position))

    def _mark_plagiarism(self, result, is_plagiarism: bool):
        """标记抄袭状态"""
        from view.history_view import PlagiarismMarkDialog
        
        dialog = PlagiarismMarkDialog(result.file_a, result.file_b, self)
        dialog.plagiarism_checkbox.setChecked(is_plagiarism)
        
        if dialog.exec_() == PlagiarismMarkDialog.Accepted:
            dialog_result = dialog.get_result()
            self.plagiarism_marked.emit(
                result.file_a, 
                result.file_b, 
                dialog_result['is_plagiarism'], 
                dialog_result['notes']
            )
            # 更新本地数据
            result.is_plagiarism = dialog_result['is_plagiarism']
            result.plagiarism_notes = dialog_result['notes']
            # 刷新视图
            self.update_view([metric for metric in result.scores.keys() if metric != "综合可疑度"])

    def _edit_notes(self, result):
        """编辑备注"""
        from view.history_view import PlagiarismMarkDialog
        
        dialog = PlagiarismMarkDialog(result.file_a, result.file_b, self)
        dialog.plagiarism_checkbox.setChecked(result.is_plagiarism)
        dialog.notes_edit.setPlainText(result.plagiarism_notes)
        
        if dialog.exec_() == PlagiarismMarkDialog.Accepted:
            dialog_result = dialog.get_result()
            self.plagiarism_marked.emit(
                result.file_a, 
                result.file_b, 
                dialog_result['is_plagiarism'], 
                dialog_result['notes']
            )
            # 更新本地数据
            result.is_plagiarism = dialog_result['is_plagiarism']
            result.plagiarism_notes = dialog_result['notes']
            # 刷新视图
            self.update_view([metric for metric in result.scores.keys() if metric != "综合可疑度"])

    def _show_notes(self, result):
        """显示备注"""
        QMessageBox.information(
            self, 
            "备注信息", 
            f"文件A: {Path(result.file_a).name}\n"
            f"文件B: {Path(result.file_b).name}\n\n"
            f"备注: {result.plagiarism_notes}"
        )