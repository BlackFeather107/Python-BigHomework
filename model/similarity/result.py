# model/similarity/result.py

from typing import List, Tuple

class ComparisonResult:
    """
    保存两份代码的相似度比较结果。
    """
    def __init__(self,
                 file_a: str,
                 file_b: str,
                 score: float,
                 segments: List[Tuple[int, int, int, int]]):
        self.file_a = file_a
        self.file_b = file_b
        self.score = score
        self.segments = segments