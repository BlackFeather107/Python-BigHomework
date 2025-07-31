# model/similarity/metrics.py

from difflib import SequenceMatcher
from typing import List

class JaccardMetric:
    """计算杰卡德相似度。"""

    def calculate(self, tokens_a: List[str], tokens_b: List[str]) -> float:
        """
        计算两组Token的Jaccard相似度。
        它衡量的是“词汇”的重合度。
        """
        set_a = set(tokens_a)
        set_b = set(tokens_b)
        
        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)

        if not union:
            return 1.0 if not intersection else 0.0

        return len(intersection) / len(union)

class LCSMetric:
    """计算最长公共子序列（LCS）比率。"""

    def calculate(self, tokens_a: List[str], tokens_b: List[str]) -> float:
        """
        计算两组Token的LCS比率。
        它衡量的是代码的“逻辑顺序”相似度。
        """
        if not tokens_a or not tokens_b:
            return 0.0
            
        # 使用动态规划计算LCS的长度
        m, n = len(tokens_a), len(tokens_b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if tokens_a[i - 1] == tokens_b[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        
        lcs_length = dp[m][n]
        return (2 * lcs_length) / (m + n)

class SequenceSimilarityMetric:
    """
    计算序列相似度。
    这与编辑距离相似，衡量的是整体内容的接近程度。
    """
    def calculate(self, tokens_a: List[str], tokens_b: List[str]) -> float:
        """
        使用SequenceMatcher的ratio()方法计算相似度。
        """
        matcher = SequenceMatcher(None, tokens_a, tokens_b)
        return matcher.ratio()
    
class LevenshteinMetric:
    """
    计算经典的编辑距离（Levenshtein Distance）并转换为相似度比率。
    """
    def calculate(self, tokens_a: List[str], tokens_b: List[str]) -> float:
        """
        计算两组Token的Levenshtein相似度比率。
        """
        len_a, len_b = len(tokens_a), len(tokens_b)

        if len_a == 0 or len_b == 0:
            return 0.0 if len_a != len_b else 1.0

        # 初始化动态规划矩阵 (dp table)
        # dp[i][j] 表示 tokens_a 的前 i 个 token 转换成 tokens_b 的前 j 个 token 所需的最小编辑距离
        dp = [[0] * (len_b + 1) for _ in range(len_a + 1)]

        for i in range(len_a + 1):
            dp[i][0] = i
        for j in range(len_b + 1):
            dp[0][j] = j

        # 填充矩阵
        for i in range(1, len_a + 1):
            for j in range(1, len_b + 1):
                # 如果 token 相同，则编辑距离不变
                cost = 0 if tokens_a[i - 1] == tokens_b[j - 1] else 1
                
                # 计算插入、删除、替换操作的成本，取最小值
                dp[i][j] = min(dp[i - 1][j] + 1,        # 删除
                               dp[i][j - 1] + 1,        # 插入
                               dp[i - 1][j - 1] + cost) # 替换

        # 计算出的编辑距离
        distance = dp[len_a][len_b]
        
        # 将距离转换为相似度比率
        # 公式: 1 - (编辑距离 / 两个序列中较长的长度)
        max_len = max(len_a, len_b)
        similarity = 1.0 - (distance / max_len)
        
        return similarity