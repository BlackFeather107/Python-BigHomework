# view/main_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QListWidget, QSplitter)
from PyQt5.QtCore import Qt
from pathlib import Path
from view.result_list import ResultListView
from view.detail_view import DetailView


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Python 代码查重工具")
        self.resize(1400, 800)

        # 主容器
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # 最左侧的文件列表面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        file_list_label = QLabel("导入的文件列表")
        self.file_list_widget = QListWidget()

        # 左下方保留区域
        placeholder_label = QLabel("（保留区域）")
        placeholder_label.setAlignment(Qt.AlignCenter)

        left_layout.addWidget(file_list_label)
        left_layout.addWidget(self.file_list_widget, 1) # 占据更多空间
        left_layout.addWidget(placeholder_label, 0)

        # 中间的结果列表面板
        self.result_list = ResultListView()
        self.result_list.item_clicked.connect(self.on_item_selected)

        # 右侧的控制与详情面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        # 导入目录按钮和运行查重按钮
        top_buttons_layout = QHBoxLayout()
        import_btn = QPushButton("导入目录")
        import_btn.clicked.connect(self.open_directory)
        analyze_btn = QPushButton("开始查重")
        # analyze_btn.clicked.connect(self.run_analysis)
        analyze_btn.clicked.connect(self.controller.trigger_analysis) # 保持对旧controller方法的连接
        top_buttons_layout.addWidget(import_btn)
        top_buttons_layout.addWidget(analyze_btn)
        right_layout.addLayout(top_buttons_layout)
        # 详细视图
        self.detail_view = DetailView()
        right_panel.addWidget(self.detail_view, 1)

        # 日志标签
        self.log_label = QLabel("状态：就绪")
        right_panel.addWidget(self.log_label)

        # 将三个面板添加到QSplitter中
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.result_list)
        main_splitter.addWidget(right_panel)
        # 设置初始比例
        main_splitter.setSizes([200, 600, 600])

        # 控制器注入视图
        self.controller.result_view = self.result_list
        self.controller.detail_view = self.detail_view

    def open_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择代码目录")
        if directory:
            self.log_label.setText(f"状态：已导入 {directory}")
            self.controller.import_directory(directory)
            
            # 更新文件列表
            self.file_list_widget.clear()
            files = self.controller.file_manager.files
            if files:
                for file_path in files:
                    self.file_list_widget.addItem(Path(file_path).name)

    def on_item_selected(self, comparison):
        # 更新状态栏，只显示文件名
        file_a_name = Path(comparison.file_a).name
        file_b_name = Path(comparison.file_b).name
        self.log_label.setText(f"状态：查看 {file_a_name} vs {file_b_name}")
        self.controller.show_detail(comparison)