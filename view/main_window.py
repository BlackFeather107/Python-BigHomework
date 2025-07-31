# view/main_window.py

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFileDialog, QLabel, QGroupBox, QCheckBox
from PyQt5.QtCore import Qt
from view.result_list import ResultListView
from view.detail_view import DetailView


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Python 代码查重工具")
        self.resize(1200, 700) # 这里稍微扩大了一些

        self.all_metrics = list(self.controller.analyzer.metrics.keys())
        self.active_metrics = self.all_metrics[:]

        # 主容器
        container = QWidget(self)
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)

        # 左侧——结果列表
        self.result_list = ResultListView()
        self.result_list.item_clicked.connect(self.on_item_selected)
        main_layout.addWidget(self.result_list, 4)

        # 右侧——详细对比
        right_panel = QVBoxLayout()
        # 导入目录按钮
        import_btn = QPushButton("导入目录")
        import_btn.clicked.connect(self.open_directory)
        right_panel.addWidget(import_btn)
        # 运行查重按钮
        top_buttons_layout = QHBoxLayout()
        analyze_btn = QPushButton("开始查重")
        analyze_btn.clicked.connect(self.run_analysis)
        top_buttons_layout.addWidget(import_btn)
        top_buttons_layout.addWidget(analyze_btn)
        right_panel.addLayout(top_buttons_layout)
        self.create_metrics_selector(right_panel)
        # 详细视图
        self.detail_view = DetailView()
        right_panel.addWidget(self.detail_view, 1)

        # 日志标签
        self.log_label = QLabel("状态：就绪")
        self.log_label.setAlignment(Qt.AlignLeft)
        right_panel.addWidget(self.log_label)

        main_layout.addLayout(right_panel, 6)

        # 控制器注入视图
        self.controller.result_view = self.result_list
        self.controller.detail_view = self.detail_view

        # 初始时更新一次视图，显示所有列
        self.result_list.update_view(self.active_metrics)

    def create_metrics_selector(self, parent_layout):
        """创建指标选择的UI组件"""
        group_box = QGroupBox("指标显示/排序控制")
        layout = QHBoxLayout()
        
        self.metric_checkboxes = {}
        for metric_name in self.all_metrics:
            checkbox = QCheckBox(metric_name)
            checkbox.setChecked(True) # 默认全部选中
            checkbox.stateChanged.connect(self.on_metric_toggled)
            self.metric_checkboxes[metric_name] = checkbox
            layout.addWidget(checkbox)
        
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)
    def on_metric_toggled(self):
        """当任何一个指标复选框状态改变时调用"""
        # 重新构建 active_metrics 列表
        new_active_metrics = []
        # 按按钮的固定顺序检查，保证基础顺序
        for metric_name in self.all_metrics:
            # 如果按钮被选中，且之前就在显示列表中，则保留其位置
            if self.metric_checkboxes[metric_name].isChecked() and metric_name in self.active_metrics:
                new_active_metrics.append(metric_name)
        
        # 找出新勾选的按钮，添加到末尾
        for metric_name in self.all_metrics:
            if self.metric_checkboxes[metric_name].isChecked() and metric_name not in new_active_metrics:
                 new_active_metrics.append(metric_name)
        
        self.active_metrics = new_active_metrics
        
        # 通知 result_list 更新视图
        self.result_list.update_view(self.active_metrics)

    def run_analysis(self):
        """执行分析并使用当前激活的指标更新视图"""
        self.log_label.setText("状态：正在分析中...")
        # 异步执行或使用QThread会更好，但为简单起见，这里直接调用
        self.controller.trigger_analysis()
        self.log_label.setText("状态：分析完成")
        # 分析完成后，使用当前的激活指标列表刷新视图
        self.result_list.update_view(self.active_metrics)

    def open_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择代码目录")
        if directory:
            self.log_label.setText(f"状态：已导入 {directory}")
            self.controller.import_directory(directory)

    def on_item_selected(self, comparison):
        # 更新状态
        self.log_label.setText(f"状态：查看 {comparison.file_a} vs {comparison.file_b}")
        self.controller.show_detail(comparison)