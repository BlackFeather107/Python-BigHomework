# model/similarity.py

from typing import List, Tuple
from difflib import SequenceMatcher
from pathlib import Path

class ComparisonResult:
    """
    保存两份代码的相似度比较结果。
    attributes:
        file_a: 文件 A 的路径字符串
        file_b: 文件 B 的路径字符串
        score: 相似度分值（0.0-1.0）
        segments: 相似片段列表，元素为 (start_a, end_a, start_b, end_b)
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

class SimilarityAnalyzer:
    """
    提供代码相似度计算接口。
    使用 difflib.SequenceMatcher 对源码字符串进行比对。
    """
    def __init__(self):
        pass

    def compute_pair(self, code_a: str, code_b: str) -> ComparisonResult:
        """
        计算两份源码的相似度，返回 ComparisonResult。
        :param code_a: 源码 A 文本
        :param code_b: 源码 B 文本
        """
        matcher = SequenceMatcher(None, code_a, code_b)
        score = matcher.ratio()
        blocks = matcher.get_matching_blocks()
        # 过滤长度为零的匹配块
        segments: List[Tuple[int,int,int,int]] = []
        for block in blocks:
            if block.size > 0:
                segments.append((block.a, block.a + block.size,
                                 block.b, block.b + block.size))
        return ComparisonResult(file_a='', file_b='', score=score, segments=segments)

    def compute_all_pairs(self, files: List[str]) -> List[ComparisonResult]:
        """
        对所有文件两两计算相似度。
        :param files: 文件路径列表（字符串）
        :return: ComparisonResult 列表，按相似度降序排列
        """
        results: List[ComparisonResult] = []
        n = len(files)
        for i in range(n):
            for j in range(i+1, n):
                path_a = files[i]
                path_b = files[j]
                # 读取源码文本
                code_a = Path(path_a).read_text(encoding='utf-8')
                code_b = Path(path_b).read_text(encoding='utf-8')
                # 计算相似度
                result = self.compute_pair(code_a, code_b)
                result.file_a = path_a
                result.file_b = path_b
                results.append(result)
        # 按 score 降序
        results.sort(key=lambda x: x.score, reverse=True)
        return results