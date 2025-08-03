# controller/main_controller.py

import uuid
from pathlib import Path
from typing import List
from datetime import datetime
from model.file_manager import FileManager
from model.similarity import CodeAnalyzer, ComparisonResult
from model.similarity.result import AnalysisSession
from model.history_manager import HistoryManager
from view.result_list import ResultListView
from view.detail_view import DetailView

class MainController:
    """
    协调 Model 与 View 的核心控制器。
    负责导入文件、执行查重、以及展示详细对比。
    """
    def __init__(self):
        # 模型
        self.file_manager = FileManager()
        self.analyzer = CodeAnalyzer()
        self.history_manager = HistoryManager()
        
        # 当前会话
        self.current_session: AnalysisSession = None
        self.login_time = datetime.now()
        
        # 视图（在 MainWindow 中注入）
        self.result_view: ResultListView = None  # type: ignore
        self.detail_view: DetailView = None      # type: ignore

    def import_directory(self, directory: str) -> None:
        """
        加载指定目录下所有的 .py 文件。
        """
        try:
            self.file_manager.load_directory(directory)
        except Exception as e:
            print(f"加载目录失败: {e}")

    def import_files(self, file_paths: List[str]) -> None:
        """
        加载指定路径的单个或多个 .py 文件。
        并将结果通知日志，由 MainWindow 接管显示。
        """
        try:
            self.file_manager.load_files(file_paths)
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

    def trigger_analysis(self) -> None:
        """
        对已加载的文件执行两两查重，按重复率降序。
        将结果传递给 ResultListView 更新显示。
        """
        files = [str(p) for p in self.file_manager.sorted_files]
        if not files:
            print("无文件可查重")
            return
        
        # 创建会话
        session_id = str(uuid.uuid4())
        session_description = f"自定义导入 ({len(files)}个文件)"
        self.current_session = AnalysisSession(
            session_id=session_id,
            directory=session_description,
            login_time=self.login_time
        )

        # 执行匹配分析
        results = self.analyzer.run_analysis(files)
        
        # 将结果添加到当前会话
        if self.current_session:
            for result in results:
                self.current_session.add_result(result)
            # 保存到历史记录
            self.history_manager.add_session(self.current_session)
        
        # 更新列表视图
        if self.result_view:
            self.result_view.set_data(results)

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
        if session and self.result_view:
            self.result_view.set_data(session.results)
            return session
        return None

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

    # 可扩展：导出报告、日志记录等方法