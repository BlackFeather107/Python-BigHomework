# model/similarity/preprocessors.py

import tokenize
from io import StringIO
from typing import List, Dict, Set, Tuple
import ast
import keyword

class AstProcessor(ast.NodeVisitor):
    """
    一个多功能的AST遍历器，负责识别并记录标识符的角色。
    """
    def __init__(self):
        self.roles: Dict[str, str] = {}
        self.keywords: Set[str] = set(keyword.kwlist)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.roles[node.name] = 'FUNC'
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.roles[node.name] = 'CLASS'
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if node.id not in self.keywords and node.id not in self.roles:
            self.roles[node.id] = 'VAR'
        self.generic_visit(node)

class Tokenizer:
    """
    负责将源代码字符串转换为用于高亮和计算的Token序列。
    """
    def process_source(self, source_code: str) -> Tuple[List[str], List[tokenize.TokenInfo]]:
        """
        处理源代码，返回一个元组：
        1. 用于计算的归一化Token字符串列表。
        2. 用于高亮的原始TokenInfo对象列表（不过滤任何东西）。
        """
        # 使用AST进行符号分析
        roles: Dict[str, str] = {}
        try:
            tree = ast.parse(source_code)
            visitor = AstProcessor()
            visitor.visit(tree)
            roles = visitor.roles
        except (SyntaxError, ValueError) as e:
            print(f"AST处理失败: {e}. 将在不进行角色归一化的情况下继续。")

        # 一次性生成两套Token列表
        tokens_for_calc = []
        tokens_for_highlight = []
        try:
            token_generator = tokenize.generate_tokens(StringIO(source_code).readline)
            for token in token_generator:
                # 高亮列表包含所有可见Token，只过滤掉对定位无意义的
                if token.type not in (tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER):
                    tokens_for_highlight.append(token)

                # 计算列表则进行深度过滤和归一化
                if token.type in (tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT,
                                  tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER):
                    continue
                
                # 忽略文档字符串和其他字符串字面量
                if token.type == tokenize.STRING:
                    continue
                
                if token.type == tokenize.NAME:
                    role = roles.get(token.string)
                    tokens_for_calc.append(role if role else token.string)
                else:
                    tokens_for_calc.append(token.string)

        except (tokenize.TokenError, IndentationError) as e:
            print(f"词法分析失败: {e}")
            return [], []
            
        return tokens_for_calc, tokens_for_highlight
