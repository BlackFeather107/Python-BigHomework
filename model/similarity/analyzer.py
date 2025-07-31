# model/similarity/analyzer.py

from pathlib import Path
from typing import List
from difflib import SequenceMatcher

from .preprocessors import Tokenizer
from .result import ComparisonResult
from .metrics import JaccardMetric, LCSMetric, SequenceSimilarityMetric, LevenshteinMetric

class CodeAnalyzer:
    """
    代码分析器，负责协调整个查重流程。
    """
    def __init__(self):
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
                path_a, path_b = files[i], files[j]

                # --- 调试打印 1: 打印正在比较的文件对 ---
                print(f"\n{'='*20} DEBUG INFO {'='*20}")
                print(f"正在比较: {Path(path_a).name}  vs  {Path(path_b).name}")
                # --- 调试打印结束 ---

                code_a = Path(path_a).read_text(encoding='utf-8')
                code_b = Path(path_b).read_text(encoding='utf-8')

                tokens_a = self.tokenizer.get_token_strings(code_a)
                tokens_b = self.tokenizer.get_token_strings(code_b)

                # --- 调试打印 2: 打印生成的Token序列（部分） ---
                print(f"  -> {Path(path_a).name} 的Token序列 (前20个): {tokens_a[:20]}")
                print(f"  -> {Path(path_b).name} 的Token序列 (前20个): {tokens_b[:20]}")
                # --- 调试打印结束 ---

                current_scores = {}
                                # --- 调试打印 3: 打印每个指标的独立计算结果 ---
                print("  -> 各指标计算结果:")
                for name, metric_calculator in self.metrics.items():
                    score = metric_calculator.calculate(tokens_a, tokens_b)
                    print(f"    - {name}: {score:.4f}") # 打印到小数点后4位
                    current_scores[name] = score
                print(f"{'='*52}")
                # --- 调试打印结束 ---

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