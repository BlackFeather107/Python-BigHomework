# view/main_window.py

from PyQt5.QtWidgets import QMainWindow, QSplitter, QFileDialog
from PyQt5.QtCore import Qt
from pathlib import Path

# 导入新的面板类
from view.panels.left_panel import LeftPanel
from view.panels.center_panel import CenterPanel
from view.panels.right_panel import RightPanel

METRIC_DESCRIPTIONS = {
    "综合可疑度": "综合所有单一指标的加权平均分，作为评估整体抄袭可能性的主要依据。",
    "逻辑顺序相似度": "衡量两份代码是否存在大量逻辑顺序相同的代码片段。此指标越高，说明一份代码很可能是从另一份直接复制并稍加修改得来的。",
    "结构指纹相似度": "通过提取代码中的核心逻辑结构（如循环、判断分支等）并生成'指纹'，来比较两份代码在架构上的相似性。此指标越高，说明代码的'骨架'越相似。",
    "词汇重合度": "衡量两份代码使用了多少相同的'词汇'（如变量名、函数名等），不考虑代码顺序。此指标越高，说明两份代码的'用词'越相似。",
    "序列匹配度": "通过寻找两份代码中最长的连续匹配块，并递归地处理剩余部分，来计算总体的匹配程度。此指标越高，说明两份代码中可以找到的相同代码片段越多、越长。",
    "语法构成相似度": "通过统计代码中各类语法元素（赋值、函数调用、算术运算等）的使用频率，来比较两份代码在编程风格和语法构成上的相似性。"
}

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Python 代码查重工具")
        self.resize(1800, 900)

        # 状态管理
        base_metrics = list(self.controller.analyzer.metrics.keys())
        self.all_metrics = ["综合可疑度"] + base_metrics
        self.active_metrics = self.all_metrics[:]

        # 创建核心UI面板
        self.left_panel = LeftPanel(controller)
        self.center_panel = CenterPanel()
        self.right_panel = RightPanel(controller, self.all_metrics, METRIC_DESCRIPTIONS)

        # 将三个面板添加到QSplitter中，链接所有信号和槽
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)
        main_splitter.addWidget(self.left_panel)
        main_splitter.addWidget(self.center_panel)
        main_splitter.addWidget(self.right_panel)
        main_splitter.setSizes([300, 900, 600])
        self._connect_signals()

        # 控制器注入视图
        self.controller.result_view = self.center_panel
        self.controller.detail_view = self.right_panel.detail_view
        self.center_panel.update_view(self.active_metrics)

    def _connect_signals(self):
        """集中管理所有信号和槽的连接。"""
        # 右侧面板信号 -> MainWindow槽函数
        self.right_panel.import_directory_clicked.connect(self.open_directory)
        self.right_panel.import_files_clicked.connect(self.open_files)
        self.right_panel.analyze_clicked.connect(self.run_analysis)
        self.right_panel.metric_toggled.connect(self.on_metric_toggled)

        # 左侧面板信号 -> MainWindow槽函数
        self.left_panel.reset_files_clicked.connect(self.on_reset_files)
        self.left_panel.file_remove_requested.connect(self.on_remove_file)
        self.left_panel.history_view.session_selected.connect(self.on_history_session_selected)
        
        # 中间面板信号 -> MainWindow槽函数
        self.center_panel.item_clicked.connect(self.on_item_selected)
        self.center_panel.plagiarism_marked.connect(self.on_plagiarism_marked)

    def on_metric_toggled(self, metric_name, state):
        """处理指标复选框状态改变"""
        if state:
            # 如果是勾选，添加到显示列表的末尾
            if metric_name not in self.active_metrics:
                self.active_metrics.append(metric_name)
        else:
            # 如果是取消勾选，从列表中移除
            if metric_name in self.active_metrics:
                self.active_metrics.remove(metric_name)
        
        # 更新视图
        self.center_panel.update_view(self.active_metrics)
        
    def run_analysis(self):
        """执行分析并使用当前激活的指标更新视图"""
        self.right_panel.log_label.setText("状态：正在分析中...")
        self.controller.trigger_analysis()
        self.right_panel.log_label.setText("状态：分析完成")
        self.center_panel.set_data(self.controller.current_session.results)
        self.center_panel.update_view(self.active_metrics)
        self.left_panel.history_view.refresh_sessions()

    def open_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择代码目录")
        if directory:
            self.right_panel.log_label.setText(f"状态：已从目录 {Path(directory).name} 添加文件")
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
            self.right_panel.log_label.setText(f"状态：已添加 {len(file_paths)} 个文件")
            self.controller.import_files(file_paths)
            self._update_file_list_ui()

    def _update_file_list_ui(self):
        """刷新文件列表UI"""
        files = self.controller.file_manager.sorted_files
        self.left_panel.update_file_list(files)

    def on_remove_file(self, file_path: Path):
        """处理单个文件移除的请求。"""
        self.controller.remove_file(file_path)
        self.right_panel.log_label.setText(f"状态：已移除文件 {file_path.name}")
        self._update_file_list_ui() # 刷新UI

    def on_reset_files(self):
        """处理重置所有文件的请求。"""
        self.controller.clear_all_files()
        self.right_panel.log_label.setText("状态：已清空所有导入的文件")
        self._update_file_list_ui() # 刷新UI

    def on_item_selected(self, comparison):
        # 更新状态栏，只显示文件名
        file_a_name = Path(comparison.file_a).name
        file_b_name = Path(comparison.file_b).name
        self.right_panel.log_label.setText(f"状态：查看 {file_a_name} vs {file_b_name}")
        self.controller.show_detail(comparison)

    def on_history_session_selected(self, session_id):
        """历史会话被选中"""
        session = self.controller.load_session(session_id)
        if session:
            self.right_panel.log_label.setText(f"状态：加载历史会话 {session.session_id[:8]}...")
            self.center_panel.set_data(session.results)
            self.center_panel.update_view(self.active_metrics)

    def on_plagiarism_marked(self, file_a, file_b, is_plagiarism, notes):
        """抄袭标记事件"""
        self.controller.mark_plagiarism(file_a, file_b, is_plagiarism, notes)
        self.right_panel.plagiarism_view.refresh_plagiarism_sessions()
        self.left_panel.history_view.refresh_sessions()
