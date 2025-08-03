# model/similarity/analyzer.py

import ast
from pathlib import Path
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

                tokens_with_info_a = self.tokenizer.get_tokens_with_info(code_a)
                tokens_with_info_b = self.tokenizer.get_tokens_with_info(code_b)

                tokens_a = self.tokenizer.get_normalized_tokens(code_a, tokens_with_info_a)
                tokens_b = self.tokenizer.get_normalized_tokens(code_b, tokens_with_info_b)

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

                # 使用归一化的Token进行匹配
                matcher = SequenceMatcher(None, tokens_a, tokens_b)
                segments = []
                for block in matcher.get_matching_blocks():
                     if block.size > 0:
                        # block.a 和 block.b 是在 normalized_tokens 列表中的起始索引
                        # block.size 是匹配的Token数量
                        
                        # 从带位置信息的列表中，找到起始Token和结束Token
                        start_token_a = tokens_with_info_a[block.a]
                        end_token_a = tokens_with_info_a[block.a + block.size - 1]
                        
                        start_token_b = tokens_with_info_b[block.b]
                        end_token_b = tokens_with_info_b[block.b + block.size - 1]

                        # 提取它们的字符位置 (line, col)
                        # TokenInfo.start 是 (line, col)，TokenInfo.end 是 (line, col)
                        # 我们需要将它们转换为绝对字符偏移量
                        start_char_a = self._pos_to_char(code_a, start_token_a.start)
                        end_char_a = self._pos_to_char(code_a, end_token_a.end)

                        start_char_b = self._pos_to_char(code_b, start_token_b.start)
                        end_char_b = self._pos_to_char(code_b, end_token_b.end)
                        
                        segments.append((start_char_a, end_char_a, start_char_b, end_char_b))
                
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

    def _pos_to_char(self, source_code: str, pos: Tuple[int, int]) -> int:
        """
        辅助函数：将 (行号, 列号) 转换为字符串中的绝对字符索引。
        """
        line, col = pos
        lines = source_code.splitlines(True) # True保留换行符
        char_offset = sum(len(l) for l in lines[:line - 1])
        char_offset += col
        return char_offset