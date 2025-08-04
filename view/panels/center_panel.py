# view/panels/center_panel.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMenu, 
                             QAction, QMessageBox, QCheckBox)
from PyQt5.QtCore import pyqtSignal, Qt
from pathlib import Path

# ResultListView 被重命名并移动到这里
class CenterPanel(QWidget):
    item_clicked = pyqtSignal(object)
    plagiarism_marked = pyqtSignal(str, str, bool, str)
    auto_marking_toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._full_results = []
        self._current_results = []
        self._active_metrics = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["文件 A", "文件 B"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_double_click)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table)

        self.auto_mark_checkbox = QCheckBox("启用自动标记功能")
        self.auto_mark_checkbox.setChecked(True)
        self.auto_mark_checkbox.stateChanged.connect(lambda state: self.auto_marking_toggled.emit(bool(state)))
        layout.addWidget(self.auto_mark_checkbox)
    
    def set_data(self, results):
        self._full_results = results
        self._current_results = [] # 重置当前结果以便重新排序

    def update_view(self, active_metrics: list):
        self._active_metrics = active_metrics
        if not self._full_results:
            self.table.setRowCount(0)
            return

        sort_key = active_metrics[0] if active_metrics else "综合可疑度"
        
        self._current_results = sorted(self._full_results, 
                                       key=lambda x: x.scores.get(sort_key, 0), 
                                       reverse=True)

        headers = ["文件 A", "文件 B"] + active_metrics + ["抄袭状态"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setRowCount(len(self._current_results))
        for row, item in enumerate(self._current_results):
            file_a_name = Path(item.file_a).name
            file_b_name = Path(item.file_b).name
            self.table.setItem(row, 0, QTableWidgetItem(file_a_name))
            self.table.setItem(row, 1, QTableWidgetItem(file_b_name))
            
            for col_idx, metric_name in enumerate(active_metrics):
                score = item.scores.get(metric_name, 0)
                score_text = f"{score * 100:.2f}%"
                self.table.setItem(row, 2 + col_idx, QTableWidgetItem(score_text))
            
            status_col_idx = 2 + len(active_metrics)
            plagiarism_status = "已标记" if item.is_plagiarism else "未标记"
            status_item = QTableWidgetItem(plagiarism_status)
            if item.is_plagiarism:
                status_item.setBackground(Qt.red)
                status_item.setForeground(Qt.white)
            self.table.setItem(row, status_col_idx, status_item)

    def _on_double_click(self, row, column):
        if 0 <= row < len(self._current_results):
            self.item_clicked.emit(self._current_results[row])

    def _show_context_menu(self, position):
        row = self.table.rowAt(position.y())
        if row < 0: return
        result = self._current_results[row]
        menu = QMenu(self)
        
        if result.is_plagiarism:
            mark_action = QAction("取消抄袭标记", self)
            mark_action.triggered.connect(lambda: self.plagiarism_marked.emit(result.file_a, result.file_b, False, result.plagiarism_notes))
        else:
            mark_action = QAction("标记为抄袭", self)
            mark_action.triggered.connect(lambda: self._open_mark_dialog(result, True))
        
        menu.addAction(mark_action)
        edit_notes_action = QAction("编辑备注", self)
        edit_notes_action.triggered.connect(lambda: self._open_mark_dialog(result, result.is_plagiarism))
        menu.addAction(edit_notes_action)
        
        if result.plagiarism_notes:
            show_notes_action = QAction("查看备注", self)
            show_notes_action.triggered.connect(lambda: self._show_notes(result))
            menu.addAction(show_notes_action)
        
        menu.exec_(self.table.mapToGlobal(position))

    def _open_mark_dialog(self, result, is_plagiarism_default):
        from view.history_view import PlagiarismMarkDialog
        dialog = PlagiarismMarkDialog(result.file_a, result.file_b, self)
        dialog.plagiarism_checkbox.setChecked(is_plagiarism_default)
        dialog.notes_edit.setPlainText(result.plagiarism_notes)
        if dialog.exec_() == PlagiarismMarkDialog.Accepted:
            dialog_result = dialog.get_result()
            self.plagiarism_marked.emit(
                result.file_a, result.file_b, 
                dialog_result['is_plagiarism'], dialog_result['notes']
            )
            # 立即更新本地数据以刷新UI
            result.is_plagiarism = dialog_result['is_plagiarism']
            result.plagiarism_notes = dialog_result['notes']
            self.update_view(self._active_metrics)

    def _show_notes(self, result):
        QMessageBox.information(self, "备注信息", f"备注: {result.plagiarism_notes}")
