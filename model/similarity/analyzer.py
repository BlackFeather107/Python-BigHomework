# model/similarity/analyzer.py

from pathlib import Path
from typing import List
from difflib import SequenceMatcher

from .preprocessors import CodeCleaner, Tokenizer
from .result import ComparisonResult
from .metrics import JaccardMetric, LCSMetric, SequenceSimilarityMetric, LevenshteinMetric

class CodeAnalyzer:
    """
    代码分析器，负责协调整个查重流程。
    """
    def __init__(self):
        self.cleaner = CodeCleaner()
        self.tokenizer = Tokenizer()
        self.metrics = {
            "词汇重合度": JaccardMetric(),
            "逻辑顺序相似度": LCSMetric(),
            "序列匹配度": SequenceSimilarityMetric(),
            "编辑距离相似度": LevenshteinMetric()
        }

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

                current_scores = {}
                for name, metric_calculator in self.metrics.items():
                    score = metric_calculator.calculate(tokens_a, tokens_b)
                    current_scores[name] = score

                # --- 临时过渡：高亮片段仍然使用SeqMatch的结果 ---
                # TODO:如果要高亮显示，高亮的位置需要映射回原始代码
                # 未来可以优化为根据不同指标显示不同高亮
                matcher = SequenceMatcher(None, tokens_a, tokens_b)
                segments = []
                for block in matcher.get_matching_blocks():
                     if block.size > 0:
                        # NOTE：这里的位置是基于Token列表的索引，而非原始代码的字符索引
                        segments.append((block.a, block.a + block.size,
                                         block.b, block.b + block.size))
                # --- 过渡结束 ---
                
                result = ComparisonResult(
                    file_a=path_a,
                    file_b=path_b,
                    scores=current_scores,
                    segments=segments 
                )
                results.append(result)

        # TODO:暂时默认为LCS，后续替换为综合指标
        default_sort_key = "逻辑顺序相似度 (LCS)"
        results.sort(key=lambda x: x.scores.get(default_sort_key, 0), reverse=True)        
        return results