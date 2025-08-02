# model/similarity/analyzer.py

import ast
from pathlib import Path
from typing import List, Dict
from difflib import SequenceMatcher

from .preprocessors import Tokenizer
from .result import ComparisonResult
from .metrics import (JaccardMetric, LCSMetric, SequenceSimilarityMetric, 
                      LevenshteinMetric, ASTFingerprintMetric, ASTHistogramMetric)

class CodeAnalyzer:
    """
    代码分析器，负责协调整个查重流程。
    """
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.metrics = {
            # "编辑距离相似度": LevenshteinMetric(),
            "逻辑顺序相似度": LCSMetric(),
            "结构指纹相似度": ASTFingerprintMetric(),
            "词汇重合度": JaccardMetric(),
            "序列匹配度": SequenceSimilarityMetric(),
            "语法构成相似度": ASTHistogramMetric()
        }
        self.weights = {
            # "编辑距离相似度": LevenshteinMetric(),
            "逻辑顺序相似度": 0.35,
            "结构指纹相似度": 0.35,
            "词汇重合度": 0.10,
            "序列匹配度": 0.10,
            "语法构成相似度": 0.10
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

                code_a = Path(path_a).read_text(encoding='utf-8')
                code_b = Path(path_b).read_text(encoding='utf-8')

                tokens_a = self.tokenizer.get_token_strings(code_a)
                tokens_b = self.tokenizer.get_token_strings(code_b)

                tree_a, tree_b = None, None
                try:
                    tree_a = ast.parse(code_a)
                    tree_b = ast.parse(code_b)
                except SyntaxError as e:
                    print(f"AST解析失败，跳过AST指标计算: {e}")

                current_scores = {}
                for name, metric_calculator in self.metrics.items():
                    score = 0.0
                    if isinstance(metric_calculator, (ASTFingerprintMetric, ASTHistogramMetric)):
                        score = metric_calculator.calculate(tree_a, tree_b)
                    else:
                        score = metric_calculator.calculate(tokens_a, tokens_b)
                    current_scores[name] = score
                
                # 将综合分也存入分数字典
                composite_score = 0.0
                for name, score in current_scores.items():
                    composite_score += score * self.weights.get(name, 0)
                
                current_scores["综合可疑度"] = composite_score

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

        default_sort_key = "综合可疑度"
        results.sort(key=lambda x: x.scores.get(default_sort_key, 0), reverse=True)        
        return results