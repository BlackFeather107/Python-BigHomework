# controller/main_controller.py

import uuid
from pathlib import Path
from typing import List, Tuple, Any
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

from model.file_manager import FileManager
from model.similarity import CodeAnalyzer, ComparisonResult
from model.similarity.result import AnalysisSession
from model.history_manager import HistoryManager
from view.panels.center_panel import CenterPanel
from view.detail_view import DetailView
from model.graph_handler import GraphHandler

class MainController(QObject):
    """
    协调 Model 与 View 的核心控制器。
    负责导入文件、执行查重、以及展示详细对比。
    """
    # 定义一个信号，用于通知MainWindow显示弹窗
    show_auto_mark_dialog_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        # 模型
        self.file_manager = FileManager()
        self.analyzer = CodeAnalyzer()
        self.history_manager = HistoryManager()
        self.graph_handler = GraphHandler()
        
        # 当前会话
        self.current_session: AnalysisSession = None
        self.login_time = datetime.now()

        # 自动标记功能的状态变量
        self.auto_marking_enabled = True
        self.suppress_auto_mark_popup = False
        self.has_shown_auto_mark_popup = False

        # 用于追踪导入来源的状态列表
        self.import_sources: List[Tuple[str, Any]] = []

        # 视图（在 MainWindow 中注入）
        self.result_view: CenterPanel = None  # type: ignore
        self.detail_view: DetailView = None      # type: ignore

    def import_directory(self, directory: str) -> None:
        """
        加载指定目录下所有的 .py 文件。
        """
        try:
            self.file_manager.load_directory(directory)
            self.import_sources.append(('dir', directory))
        except Exception as e:
            print(f"加载目录失败: {e}")

    def import_files(self, file_paths: List[str]) -> None:
        """
        加载指定路径的单个或多个 .py 文件。
        并将结果通知日志，由 MainWindow 接管显示。
        """
        try:
            self.file_manager.load_files(file_paths)
            self.import_sources.append(('files', file_paths))
        except Exception as e:
            print(f"加载目录失败: {e}")

    def remove_file(self, file_path: Path):
        """
        移除一个文件。
        """
        self.file_manager.remove_file(file_path)

    def clear_all_files(self):
        """
        清空所有文件。
        """
        self.file_manager.clear_all()
        self.import_sources.clear()

    # 用于从UI更新弹窗状态
    def set_auto_marking_enabled(self, enabled: bool):
        self.auto_marking_enabled = enabled

    def set_suppress_popup(self, suppress: bool):
        self.suppress_auto_mark_popup = suppress

    def clear_all_markings(self):
        """清除当前会话中所有结果的抄袭标记。"""
        if not self.current_session:
            return

        for result in self.current_session.results:
            result.is_plagiarism = False
            result.plagiarism_notes = ""
        
        # 更新历史记录中的会话数据
        self.history_manager.add_session(self.current_session)

    def trigger_analysis(self) -> None:
        """
        对已加载的文件执行两两查重，按重复率降序。
        将结果传递给 ResultListView 更新显示。
        """
        files = [str(p) for p in self.file_manager.sorted_files]
        if not files:
            print("无文件可查重")
            if self.result_view:
                self.result_view.set_data([])
                self.result_view.update_view([])
            return
        
        # 创建会话
        session_id = str(uuid.uuid4())
        session_description = ""
        if hasattr(self, 'import_sources') and len(self.import_sources) == 1 and self.import_sources[0][0] == 'dir':
            # 如果只有一次导入，且是目录导入
            directory_path = self.import_sources[0][1]
            session_description = f"从 {Path(directory_path).name} 导入 ({len(files)}个文件)"
        else:
            # 其他所有情况（多次导入、仅文件导入、混合导入）
            session_description = f"自定义导入 ({len(files)}个文件)"
        self.current_session = AnalysisSession(
            session_id=session_id,
            directory=session_description,
            login_time=self.login_time
        )

        # 执行匹配分析
        results = self.analyzer.run_analysis(files)
        
        # 执行自动标记
        auto_marked_count = 0
        if self.auto_marking_enabled:
            for result in results:
                # 只标记之前未被标记过的
                if not result.is_plagiarism and result.scores.get("综合可疑度", 0) >= 0.80:
                    result.is_plagiarism = True
                    result.plagiarism_notes = "自动标记 (可疑度 >= 80%)"
                    auto_marked_count += 1
        
        # 检查是否需要弹窗
        if auto_marked_count > 0 and not self.suppress_auto_mark_popup and not self.has_shown_auto_mark_popup:
            self.has_shown_auto_mark_popup = True
            self.show_auto_mark_dialog_requested.emit() # 发射信号

        # 将结果添加到当前会话
        if self.current_session:
            for result in results:
                self.current_session.add_result(result)
            # 保存到历史记录
            self.history_manager.add_session(self.current_session)
        
        # 更新列表视图
        if self.result_view:
            self.result_view.set_data(results)
        
        # 分析完成后清空本次的导入来源记录
        if hasattr(self, 'import_source'):
            self.import_sources.clear()

    def show_detail(self, comparison: ComparisonResult) -> None:
        """
        接收用户点击的 ComparisonResult，调用 DetailView 展示高亮对比。
        """
        if self.detail_view:
            self.detail_view.show(comparison)

    def get_login_time(self) -> datetime:
        """
        获取登录时间
        """
        return self.login_time

    def get_all_sessions(self):
        """
        获取所有历史会话
        """
        return self.history_manager.get_all_sessions()

    def load_session(self, session_id: str):
        """
        加载指定的历史会话
        """
        session = self.history_manager.get_session_by_id(session_id)
        if session:
            self.current_session = session
            if self.result_view:
                self.result_view.set_data(session.results)
        return session

    def mark_plagiarism(self, file_a: str, file_b: str, is_plagiarism: bool, notes: str = ""):
        """
        标记抄袭状态
        """
        if self.current_session:
            self.history_manager.update_result_plagiarism_status(
                self.current_session.session_id,
                file_a, file_b, is_plagiarism, notes
            )

    def export_plagiarism_report(self, output_file: str) -> bool:
        """
        导出抄袭报告
        """
        return self.history_manager.export_plagiarism_report(output_file)

    def export_plagiarism_files(self, output_dir: str) -> bool:
        """
        导出抄袭文件
        """
        return self.history_manager.export_plagiarism_files(output_dir)

    def get_plagiarism_sessions(self):
        """
        获取包含抄袭判定的会话
        """
        return self.history_manager.get_plagiarism_sessions()

    def view_plagiarism_graph(self):
        """创建并显示抄袭关系图。"""
        if self.current_session and self.current_session.results:
            graph = self.graph_handler.create_graph(self.current_session.results)
            self.graph_handler.draw_graph(graph)
        else:
            print("没有可用于生成图表的查重结果。")

    def export_plagiarism_graph(self, file_path: str) -> bool:
        """创建并导出抄袭关系图。"""
        if self.current_session and self.current_session.results:
            graph = self.graph_handler.create_graph(self.current_session.results)
            return self.graph_handler.draw_graph(graph, output_path=file_path)
        return False