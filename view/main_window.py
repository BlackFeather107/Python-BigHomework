# view/main_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QGroupBox, 
                             QCheckBox, QListWidget, QSplitter)
from PyQt5.QtCore import Qt
from pathlib import Path

from view.result_list import ResultListView
from view.detail_view import DetailView

METRIC_DESCRIPTIONS = {
    "综合可疑度": "综合所有单一指标的加权平均分，作为评估整体抄袭可能性的主要依据。",
    "逻辑顺序相似度": "衡量两份代码是否存在大量逻辑顺序相同的代码片段。此指标越高，说明一份代码很可能是从另一份直接复制并稍加修改得来的。",
    "结构指纹相似度": "通过提取代码中的核心逻辑结构（如循环、判断分支等）并生成“指纹”，来比较两份代码在架构上的相似性。此指标越高，说明代码的“骨架”越相似。",
    "词汇重合度": "衡量两份代码使用了多少相同的“词汇”（如变量名、函数名等），不考虑代码顺序。此指标越高，说明两份代码的“用词”越相似。",
    "序列匹配度": "通过寻找两份代码中最长的连续匹配块，并递归地处理剩余部分，来计算总体的匹配程度。此指标越高，说明两份代码中可以找到的相同代码片段越多、越长。",
    "语法构成相似度": "通过统计代码中各类语法元素（赋值、函数调用、算术运算等）的使用频率，来比较两份代码在编程风格和语法构成上的相似性。"
}

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Python 代码查重工具")
        self.resize(1400, 800)

        base_metrics = list(self.controller.analyzer.metrics.keys())
        self.all_metrics = ["综合可疑度"] + base_metrics
        self.active_metrics = self.all_metrics[:]

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
        analyze_btn.clicked.connect(self.run_analysis)
        top_buttons_layout.addWidget(import_btn)
        top_buttons_layout.addWidget(analyze_btn)
        right_layout.addLayout(top_buttons_layout)
        # 指标选择器
        self.create_metrics_selector(right_layout)
        # 详细视图
        self.detail_view = DetailView()
        right_layout.addWidget(self.detail_view, 1)

        # 日志标签
        self.log_label = QLabel("状态：就绪")
        right_layout.addWidget(self.log_label)

        # 将三个面板添加到QSplitter中
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.result_list)
        main_splitter.addWidget(right_panel)
        # 设置初始比例
        main_splitter.setSizes([200, 600, 600])

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
            display_name = metric_name.split('(')[0].strip()
            checkbox = QCheckBox(display_name)
            checkbox.setChecked(True) # 默认全部选中
            description = METRIC_DESCRIPTIONS.get(display_name, "暂无简介")
            checkbox.setToolTip(description) # 添加Tooltip
            checkbox.stateChanged.connect(
                lambda state, name=metric_name: self.on_metric_toggled(name, state)
            )
            self.metric_checkboxes[metric_name] = checkbox
            layout.addWidget(checkbox)
        
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def on_metric_toggled(self, metric_name, state):
        """当任何一个指标复选框状态改变时调用"""
        if state == Qt.Checked:
            # 如果是勾选，添加到显示列表的末尾
            if metric_name not in self.active_metrics:
                self.active_metrics.append(metric_name)
        else:
            # 如果是取消勾选，从列表中移除
            if metric_name in self.active_metrics:
                self.active_metrics.remove(metric_name)
        
        # 通知 result_list 更新视图
        self.result_list.update_view(self.active_metrics)
        
    def run_analysis(self):
        """执行分析并使用当前激活的指标更新视图"""
        self.log_label.setText("状态：正在分析中...")
        self.controller.trigger_analysis()
        self.log_label.setText("状态：分析完成")
        self.result_list.update_view(self.active_metrics)

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