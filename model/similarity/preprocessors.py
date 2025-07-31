# model/similarity/preprocessors.py

import tokenize
from io import StringIO
from typing import List
import ast

class DocstringRemover(ast.NodeTransformer):
    """
    一个AST遍历器，专门用于查找并移除函数、类和模块中的文档字符串节点。
    """
    def _remove_docstring(self, node):
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            # 如果节点的第一个子元素是一个字符串表达式，它就是文档字符串，移除它
            node.body = node.body[1:]
        
    def visit_FunctionDef(self, node):
        self._remove_docstring(node)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        self._remove_docstring(node)
        self.generic_visit(node)
        return node

    def visit_Module(self, node):
        self._remove_docstring(node)
        self.generic_visit(node)
        return node

class Tokenizer:
    """
    负责将原始源代码字符串直接转换为一个干净、过滤后的Token序列。
    """
    def get_token_strings(self, source_code: str) -> List[str]:
        """
        接收原始源代码，移除文档字符串，然后返回一个只包含Token字符串的列表。
        """
        # 步骤 1: 使用AST移除文档字符串
        source_without_docstrings = source_code
        try:
            tree = ast.parse(source_code)
            transformer = DocstringRemover()
            transformer.visit(tree)
            # 将修改后的AST转换回代码字符串 (此功能在Python 3.9+版本可用)
            source_without_docstrings = ast.unparse(tree)
        except (SyntaxError, ValueError) as e:
            # 如果代码无法被AST解析(例如有语法错误)，则打印错误并退回到原始代码
            print(f"AST解析失败: {e}. 将在不移除文档字符串的情况下继续。")

        # 步骤 2: 使用tokenize处理没有文档字符串的代码
        token_strings = []
        try:
            token_generator = tokenize.generate_tokens(StringIO(source_without_docstrings).readline)
            
            for token in token_generator:
                if token.type in (
                    tokenize.ENCODING,
                    tokenize.COMMENT, # 仍然需要移除单行注释
                    tokenize.NL,
                    tokenize.NEWLINE,
                    tokenize.INDENT,
                    tokenize.DEDENT,
                    tokenize.ENDMARKER
                ):
                    continue
                
                token_strings.append(token.string)

        except (tokenize.TokenError, IndentationError) as e:
            print(f"词法分析失败: {e}")
            return []
            
        return token_strings