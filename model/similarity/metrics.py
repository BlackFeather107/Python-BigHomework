# model/similarity/metrics.py

from difflib import SequenceMatcher
from typing import List, Tuple

class DifflibMetric:
    """使用 difflib.SequenceMatcher 计算相似度的指标类。"""

    def calculate(self, code_a: str, code_b: str) -> Tuple[float, List[Tuple[int, int, int, int]]]:
        """
        计算两份源码的相似度。
        :return: 一个元组，包含 (相似度分数, 相似片段列表)
        """
        matcher = SequenceMatcher(None, code_a, code_b)
        score = matcher.ratio()
        
        blocks = matcher.get_matching_blocks()
        segments: List[Tuple[int, int, int, int]] = []
        for block in blocks:
            if block.size > 0:
                segments.append((block.a, block.a + block.size,
                                 block.b, block.b + block.size))
        
        return score, segments