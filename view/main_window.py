# view/main_window.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QGroupBox, 
                             QCheckBox, QListWidget, QSplitter, QTabWidget,
                             QListWidgetItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from pathlib import Path

from view.result_list import ResultListView
from view.detail_view import DetailView
from view.history_view import HistoryView, PlagiarismManagementView

METRIC_DESCRIPTIONS = {
    "综合可疑度": "综合所有单一指标的加权平均分，作为评估整体抄袭可能性的主要依据。",
    "逻辑顺序相似度": "衡量两份代码是否存在大量逻辑顺序相同的代码片段。此指标越高，说明一份代码很可能是从另一份直接复制并稍加修改得来的。",
    "结构指纹相似度": "通过提取代码中的核心逻辑结构（如循环、判断分支等）并生成'指纹'，来比较两份代码在架构上的相似性。此指标越高，说明代码的'骨架'越相似。",
    "词汇重合度": "衡量两份代码使用了多少相同的'词汇'（如变量名、函数名等），不考虑代码顺序。此指标越高，说明两份代码的'用词'越相似。",
    "序列匹配度": "通过寻找两份代码中最长的连续匹配块，并递归地处理剩余部分，来计算总体的匹配程度。此指标越高，说明两份代码中可以找到的相同代码片段越多、越长。",
    "语法构成相似度": "通过统计代码中各类语法元素（赋值、函数调用、算术运算等）的使用频率，来比较两份代码在编程风格和语法构成上的相似性。"
}

# 自定义列表项Widget
class FileListItemWidget(QWidget):
    """自定义的列表项，包含文件名和一个删除按钮。"""
    remove_clicked = pyqtSignal(Path)

    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2) # 紧凑布局
        
        # 文件名标签
        self.label = QLabel(file_path.name)
        self.label.setToolTip(str(file_path)) # 悬停显示完整路径
        
        # 删除按钮
        self.remove_btn = QPushButton("✕") # 使用 "✕" 字符
        self.remove_btn.setFixedSize(20, 20) # 小尺寸按钮
        self.remove_btn.setStyleSheet("color: red; border: none; font-weight: bold;")
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.clicked.connect(self.on_remove)
        
        layout.addWidget(self.label)
        layout.addStretch() # 添加伸缩，将按钮推到最右侧
        layout.addWidget(self.remove_btn)

    def on_remove(self):
        self.remove_clicked.emit(self.file_path)

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Python 代码查重工具")
        self.resize(1600, 900)

        base_metrics = list(self.controller.analyzer.metrics.keys())
        self.all_metrics = ["综合可疑度"] + base_metrics
        self.active_metrics = self.all_metrics[:]

        # 主容器
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # 左上方文件列表面板区域
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        file_list_label = QLabel("导入的文件列表")
        self.file_list_widget = QListWidget()

        self.reset_btn = QPushButton("重置所有导入")
        self.reset_btn.clicked.connect(self.on_reset_files)

        # 左下方历史记录区域
        history_label = QLabel("历史记录")
        self.history_view = HistoryView(controller)
        self.history_view.session_selected.connect(self.on_history_session_selected)
        
        left_layout.addWidget(file_list_label)
        left_layout.addWidget(self.file_list_widget, 1) # 占据更多空间
        left_layout.addWidget(self.reset_btn)
        left_layout.addWidget(history_label)
        left_layout.addWidget(self.history_view, 1)

        # 中间的结果列表面板
        self.result_list = ResultListView()
        self.result_list.item_clicked.connect(self.on_item_selected)
        self.result_list.plagiarism_marked.connect(self.on_plagiarism_marked)

        # 右侧的控制与详情面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # 导入目录按钮、导入文件按钮和运行查重按钮
        top_buttons_layout = QHBoxLayout()
        import_dir_btn = QPushButton("导入目录")
        import_dir_btn.clicked.connect(self.open_directory)
        import_files_btn = QPushButton("导入文件")
        import_files_btn.clicked.connect(self.open_files)
        analyze_btn = QPushButton("开始查重")
        analyze_btn.clicked.connect(self.run_analysis)
        top_buttons_layout.addWidget(import_dir_btn)
        top_buttons_layout.addWidget(import_files_btn)
        top_buttons_layout.addWidget(analyze_btn)
        right_layout.addLayout(top_buttons_layout)
        
        # 指标选择器
        self.create_metrics_selector(right_layout)
        
        # 使用标签页组织详情视图和抄袭管理
        detail_tabs = QTabWidget()
        
        # 详细视图标签页
        self.detail_view = DetailView()
        detail_tabs.addTab(self.detail_view, "代码对比")
        
        # 抄袭管理标签页
        self.plagiarism_view = PlagiarismManagementView(controller)
        detail_tabs.addTab(self.plagiarism_view, "抄袭管理")
        
        right_layout.addWidget(detail_tabs, 1)

        # 日志标签
        self.log_label = QLabel("状态：就绪")
        right_layout.addWidget(self.log_label)

        # 将三个面板添加到QSplitter中
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.result_list)
        main_splitter.addWidget(right_panel)
        # 设置初始比例
        main_splitter.setSizes([300, 700, 600])

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
        # 刷新历史记录
        self.history_view.refresh_sessions()

    def open_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择代码目录")
        if directory:
            self.log_label.setText(f"状态：已从目录 {Path(directory).name} 添加文件")
            self.controller.import_directory(directory)
            self._update_file_list_ui()

    def open_files(self):
        """打开文件对话框以选择一个或多个文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "选择一个或多个Python文件", 
            "", 
            "Python 文件 (*.py)"
        )
        if file_paths:
            self.log_label.setText(f"状态：已添加 {len(file_paths)} 个文件")
            self.controller.import_files(file_paths)
            self._update_file_list_ui()

    def _update_file_list_ui(self):
        """使用自定义Widget刷新文件列表。"""
        self.file_list_widget.clear()
        files = self.controller.file_manager.sorted_files
        if files:
            for file_path in files:
                # 创建自定义Widget
                item_widget = FileListItemWidget(file_path)
                # 将自定义Widget的信号连接到处理函数
                item_widget.remove_clicked.connect(self.on_remove_file)
                
                # 创建QListWidgetItem并设置其自定义Widget
                list_item = QListWidgetItem(self.file_list_widget)
                list_item.setSizeHint(item_widget.sizeHint())
                self.file_list_widget.addItem(list_item)
                self.file_list_widget.setItemWidget(list_item, item_widget)

    def on_remove_file(self, file_path: Path):
        """处理单个文件移除的请求。"""
        self.controller.remove_file(file_path)
        self.log_label.setText(f"状态：已移除文件 {file_path.name}")
        self._update_file_list_ui() # 刷新UI

    def on_reset_files(self):
        """处理重置所有文件的请求。"""
        self.controller.clear_all_files()
        self.log_label.setText("状态：已清空所有导入的文件")
        self._update_file_list_ui() # 刷新UI

    def on_item_selected(self, comparison):
        # 更新状态栏，只显示文件名
        file_a_name = Path(comparison.file_a).name
        file_b_name = Path(comparison.file_b).name
        self.log_label.setText(f"状态：查看 {file_a_name} vs {file_b_name}")
        self.controller.show_detail(comparison)

    def on_history_session_selected(self, session_id):
        """历史会话被选中"""
        session = self.controller.load_session(session_id)
        if session:
            self.log_label.setText(f"状态：加载历史会话 {session.session_id[:8]}...")
            self.result_list.update_view(self.active_metrics)

    def on_plagiarism_marked(self, file_a, file_b, is_plagiarism, notes):
        """抄袭标记事件"""
        self.controller.mark_plagiarism(file_a, file_b, is_plagiarism, notes)
        # 刷新抄袭管理视图
        self.plagiarism_view.refresh_plagiarism_sessions()
        # 刷新历史记录
        self.history_view.refresh_sessions()
