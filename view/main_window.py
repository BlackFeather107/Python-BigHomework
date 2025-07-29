# view/main_window.py

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, QLabel
from PyQt5.QtCore import Qt
from view.result_list import ResultListView
from view.detail_view import DetailView


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Python 代码查重工具")
        self.resize(1000, 600)

        # 主容器
        container = QWidget(self)
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)

        # 左侧——结果列表
        self.result_list = ResultListView()
        self.result_list.item_clicked.connect(self.on_item_selected)
        main_layout.addWidget(self.result_list, 3)

        # 右侧——详细对比
        right_panel = QVBoxLayout()
        # 导入目录按钮
        import_btn = QPushButton("导入目录")
        import_btn.clicked.connect(self.open_directory)
        right_panel.addWidget(import_btn)
        # 运行查重按钮
        analyze_btn = QPushButton("开始查重")
        analyze_btn.clicked.connect(self.controller.trigger_analysis)
        right_panel.addWidget(analyze_btn)
        # 详细视图
        self.detail_view = DetailView()
        right_panel.addWidget(self.detail_view, 1)

        # 日志标签
        self.log_label = QLabel("状态：就绪")
        self.log_label.setAlignment(Qt.AlignLeft)
        right_panel.addWidget(self.log_label)

        main_layout.addLayout(right_panel, 7)

        # 控制器注入视图
        self.controller.result_view = self.result_list
        self.controller.detail_view = self.detail_view

    def open_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择代码目录")
        if directory:
            self.log_label.setText(f"状态：已导入 {directory}")
            self.controller.import_directory(directory)

    def on_item_selected(self, comparison):
        # 更新状态
        self.log_label.setText(f"状态：查看 {comparison.file_a} vs {comparison.file_b}")
        self.controller.show_detail(comparison)