# view/panels/left_panel.py

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                             QLabel, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from pathlib import Path

from view.history_view import HistoryView

class FileListItemWidget(QWidget):
    """自定义的列表项，包含文件名和一个删除按钮。"""
    remove_clicked = pyqtSignal(Path)

    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        self.label = QLabel(file_path.name)
        self.label.setToolTip(str(file_path))
        self.remove_btn = QPushButton("✕")
        self.remove_btn.setFixedSize(20, 20)
        self.remove_btn.setStyleSheet("color: red; border: none; font-weight: bold;")
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.file_path))
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.remove_btn)

class LeftPanel(QWidget):
    """主窗口的左侧面板，负责文件列表和历史记录。"""
    # 定义面板级别的信号
    reset_files_clicked = pyqtSignal()
    file_remove_requested = pyqtSignal(Path)
    history_session_selected = pyqtSignal(str)

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        file_list_label = QLabel("导入的文件列表")
        self.file_list_widget = QListWidget()
        
        self.reset_btn = QPushButton("重置所有导入")
        self.reset_btn.clicked.connect(self.reset_files_clicked) # 连接到面板信号
        
        history_label = QLabel("历史记录")
        self.history_view = HistoryView(self.controller)
        self.history_view.session_selected.connect(self.history_session_selected) # 连接到面板信号
        
        layout.addWidget(file_list_label)
        layout.addWidget(self.file_list_widget, 1)
        layout.addWidget(self.reset_btn)
        layout.addWidget(history_label)
        layout.addWidget(self.history_view, 1)
    
    def update_file_list(self, files: list):
        """使用自定义Widget刷新文件列表，并连接信号。"""
        self.file_list_widget.clear()
        if files:
            for file_path in files:
                item_widget = FileListItemWidget(file_path)
                item_widget.remove_clicked.connect(self.file_remove_requested) # 连接到面板信号
                
                list_item = QListWidgetItem(self.file_list_widget)
                list_item.setSizeHint(item_widget.sizeHint())
                self.file_list_widget.addItem(list_item)
                self.file_list_widget.setItemWidget(list_item, item_widget)
