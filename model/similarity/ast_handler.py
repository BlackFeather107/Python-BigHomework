# model/similarity/ast_handler.py

import ast
import hashlib
from collections import Counter
from typing import Set, Dict

class FingerprintVisitor(ast.NodeVisitor):
    """
    遍历AST，为关键结构节点生成“指纹”。
    """
    def __init__(self):
        self.fingerprints: Set[str] = set()
        # 我们关心的结构性节点
        self.target_nodes = (
            ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
            ast.For, ast.While, ast.If, ast.With, ast.Try
        )

    def generic_visit(self, node: ast.AST):
        # 只处理我们关心的目标节点
        if isinstance(node, self.target_nodes):
            # 规范化节点类型名称，例如 'FunctionDef' -> 'function'
            node_type = type(node).__name__.lower().replace('def', '')
            
            # 创建一个简单的结构表示
            # 例如 "function:if:for" 表示一个函数里有一个if和一个for
            # 这是一个简化的指纹，更复杂的可以包含子节点数量等
            structure_str = node_type
            
            # 生成哈希指纹
            hasher = hashlib.md5()
            hasher.update(structure_str.encode('utf-8'))
            self.fingerprints.add(hasher.hexdigest())

        super().generic_visit(node)

class HistogramVisitor(ast.NodeVisitor):
    """
    遍历AST，统计各类节点的出现次数，生成直方图。
    """
    def __init__(self):
        self.histogram: Counter = Counter()

    def generic_visit(self, node: ast.AST):
        # 获取节点类型名称并计数
        node_type = type(node).__name__
        self.histogram[node_type] += 1
        super().generic_visit(node)

def get_ast_fingerprints(tree: ast.AST) -> Set[str]:
    """辅助函数：获取AST的结构指纹集合。"""
    visitor = FingerprintVisitor()
    visitor.visit(tree)
    return visitor.fingerprints

def get_ast_histogram(tree: ast.AST) -> Dict[str, int]:
    """辅助函数：获取AST的节点类型直方图。"""
    visitor = HistogramVisitor()
    visitor.visit(tree)
    return dict(visitor.histogram)
