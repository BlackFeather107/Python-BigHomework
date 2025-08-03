# view/panels/right_panel.py

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QCheckBox, QTabWidget)
from PyQt5.QtCore import pyqtSignal

from view.detail_view import DetailView
from view.history_view import PlagiarismManagementView

class RightPanel(QWidget):
    """主窗口的右侧面板，负责控制和详情展示。"""
    # 定义面板级别的信号
    import_directory_clicked = pyqtSignal()
    import_files_clicked = pyqtSignal()
    analyze_clicked = pyqtSignal()
    metric_toggled = pyqtSignal(str, bool) # name, state

    def __init__(self, controller, all_metrics, metric_descriptions, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.all_metrics = all_metrics
        self.metric_descriptions = metric_descriptions
        self.metric_checkboxes = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 顶部按钮
        top_buttons_layout = QHBoxLayout()
        self.import_dir_btn = QPushButton("导入目录")
        self.import_dir_btn.clicked.connect(self.import_directory_clicked)
        self.import_files_btn = QPushButton("导入文件")
        self.import_files_btn.clicked.connect(self.import_files_clicked)
        self.analyze_btn = QPushButton("开始查重")
        self.analyze_btn.clicked.connect(self.analyze_clicked)
        top_buttons_layout.addWidget(self.import_dir_btn)
        top_buttons_layout.addWidget(self.import_files_btn)
        top_buttons_layout.addWidget(self.analyze_btn)
        layout.addLayout(top_buttons_layout)
        
        # 指标选择器
        self._create_metrics_selector(layout)
        
        # 详情标签页
        detail_tabs = QTabWidget()
        self.detail_view = DetailView()
        self.plagiarism_view = PlagiarismManagementView(self.controller)
        detail_tabs.addTab(self.detail_view, "代码对比")
        detail_tabs.addTab(self.plagiarism_view, "抄袭管理")
        layout.addWidget(detail_tabs, 1)

        # 状态日志
        self.log_label = QLabel("状态：就绪")
        layout.addWidget(self.log_label)

    def _create_metrics_selector(self, parent_layout):
        group_box = QGroupBox("指标显示/排序控制")
        layout = QHBoxLayout()
        
        for metric_name in self.all_metrics:
            display_name = metric_name.split('(')[0].strip()
            checkbox = QCheckBox(display_name)
            checkbox.setChecked(True)
            description = self.metric_descriptions.get(display_name, "暂无简介")
            checkbox.setToolTip(description)
            # 连接到面板信号
            checkbox.stateChanged.connect(
                lambda state, name=metric_name: self.metric_toggled.emit(name, bool(state))
            )
            self.metric_checkboxes[metric_name] = checkbox
            layout.addWidget(checkbox)
        
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)
