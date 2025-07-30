# model/similarity/analyzer.py

from pathlib import Path
from typing import List

from .preprocessors import CodeCleaner, Tokenizer
from .result import ComparisonResult
from .metrics import DifflibMetric

class CodeAnalyzer:
    """
    代码分析器，负责协调整个查重流程。
    """
    def __init__(self):
        self.cleaner = CodeCleaner()
        self.tokenizer = Tokenizer()
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
                
                cleaned_a = self.cleaner.clean(code_a)
                cleaned_b = self.cleaner.clean(code_b)

                tokens_a = self.tokenizer.tokenize(cleaned_a)
                tokens_b = self.tokenizer.tokenize(cleaned_b)

                '''
                token_str_a = " ".join([tok.string for tok in tokens_a])
                token_str_b = " ".join([tok.string for tok in tokens_b])
                '''
                
                # NOTE：使用清理后的代码进行相似度计算，这是一个过渡步骤
                # 实际应该使用词法分析后的序列化列表评估
                # TODO:未来的新指标(如Jaccard)将直接使用tokens_a/b列表。
                score, segments = self.metric.calculate(cleaned_a, cleaned_b)
                
                # TODO:如果要高亮显示，高亮的位置需要映射回原始代码，这是后续优化的点
                result = ComparisonResult(
                    file_a=path_a,
                    file_b=path_b,
                    score=score,
                    # 目前segments是基于清理后代码的，暂时保留
                    segments=segments 
                )
                results.append(result)

        results.sort(key=lambda x: x.score, reverse=True)
        return results