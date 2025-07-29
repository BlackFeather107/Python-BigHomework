# controller/main_controller.py

from pathlib import Path
from model.file_manager import FileManager
from model.similarity import SimilarityAnalyzer, ComparisonResult
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
        self.analyzer = SimilarityAnalyzer()
        # 视图（在 MainWindow 中注入）
        self.result_view: ResultListView = None  # type: ignore
        self.detail_view: DetailView = None      # type: ignore

    def import_directory(self, directory: str) -> None:
        """
        加载指定目录下所有的 .py 文件。
        并将结果通知日志，由 MainWindow 接管显示。
        """
        try:
            self.file_manager.load_directory(directory)
        except Exception as e:
            # 视图层可扩展 error handling
            print(f"加载目录失败: {e}")

    def trigger_analysis(self) -> None:
        """
        对已加载的文件执行两两查重，按重复率降序。
        将结果传递给 ResultListView 更新显示。
        """
        files = [str(p) for p in self.file_manager.files]
        if not files:
            print("无文件可查重")
            return
        # 执行匹配分析
        results: list[ComparisonResult] = self.analyzer.compute_all_pairs(files)
        # 更新列表视图
        if self.result_view:
            self.result_view.display(results)

    def show_detail(self, comparison: ComparisonResult) -> None:
        """
        接收用户点击的 ComparisonResult，调用 DetailView 展示高亮对比。
        """
        if self.detail_view:
            self.detail_view.show(comparison)

    # 可扩展：导出报告、日志记录等方法