# model/similarity/analyzer.py

import ast
from pathlib import Path
import tokenize
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
from datetime import datetime

from .preprocessors import Tokenizer
from .result import ComparisonResult
from .metrics import (JaccardMetric, LCSMetric, SequenceSimilarityMetric, 
                      ASTFingerprintMetric, ASTHistogramMetric)

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

                tokens_for_calc_a, tokens_for_highlight_a = self.tokenizer.process_source(code_a)
                tokens_for_calc_b, tokens_for_highlight_b = self.tokenizer.process_source(code_b)

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
                        score = metric_calculator.calculate(tokens_for_calc_a, tokens_for_calc_b)
                    current_scores[name] = score
                
                # 将综合分也存入分数字典
                composite_score = 0.0
                for name, score in current_scores.items():
                    composite_score += score * self.weights.get(name, 0)
                
                current_scores["综合可疑度"] = composite_score

                # 匹配应高亮的部分
                highlight_strings_a = [tok.string for tok in tokens_for_highlight_a]
                highlight_strings_b = [tok.string for tok in tokens_for_highlight_b]
                
                matcher = SequenceMatcher(None, highlight_strings_a, highlight_strings_b)
                segments = []
                for block in matcher.get_matching_blocks():
                     if block.size > 0:
                        # 现在 block.a 和 block.b 的索引可以直接用于 tokens_for_highlight 列表
                        start_token_a = tokens_for_highlight_a[block.a]
                        end_token_a = tokens_for_highlight_a[block.a + block.size - 1]
                        
                        start_token_b = tokens_for_highlight_b[block.b]
                        end_token_b = tokens_for_highlight_b[block.b + block.size - 1]
                        
                        segments.append((
                            start_token_a.start, end_token_a.end,
                            start_token_b.start, end_token_b.end
                        ))
                
                result = ComparisonResult(
                    file_a=path_a,
                    file_b=path_b,
                    scores=current_scores,
                    segments=segments,
                    analysis_time=datetime.now()
                )
                results.append(result)

        default_sort_key = "综合可疑度"
        results.sort(key=lambda x: x.scores.get(default_sort_key, 0), reverse=True)        
        return results

    def _create_token_map(self, highlight_tokens: List[tokenize.TokenInfo]) -> List[int]:
        """
        创建一个从计算Token索引到高亮Token索引的映射。
        """
        mapping = []
        for i, token in enumerate(highlight_tokens):
            if token.type not in (tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT, tokenize.STRING):
                mapping.append(i)
        return mapping