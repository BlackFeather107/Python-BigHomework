# model/similarity/analyzer.py

from pathlib import Path
from typing import List

# 从当前包（similarity）内导入我们刚刚创建的模块
from .result import ComparisonResult
from .metrics import DifflibMetric

class CodeAnalyzer:
    """
    代码分析器，负责协调整个查重流程。
    """
    def __init__(self):
        # 初始化时，就指定使用 DifflibMetric
        self.metric = DifflibMetric()

    def run_analysis(self, files: List[str]) -> List[ComparisonResult]:
        """
        对所有文件两两计算相似度。
        """
        results: List[ComparisonResult] = []
        n = len(files)

        for i in range(n):
            for j in range(i + 1, n):
                path_a = files[i]
                path_b = files[j]

                code_a = Path(path_a).read_text(encoding='utf-8')
                code_b = Path(path_b).read_text(encoding='utf-8')

                # 调用指标模块进行计算
                score, segments = self.metric.calculate(code_a, code_b)
                
                # 组装成 ComparisonResult 对象
                result = ComparisonResult(
                    file_a=path_a,
                    file_b=path_b,
                    score=score,
                    segments=segments
                )
                results.append(result)

        results.sort(key=lambda x: x.score, reverse=True)
        return results