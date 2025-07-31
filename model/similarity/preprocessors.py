# model/similarity/preprocessors.py

import re
from io import StringIO
import tokenize
from typing import List

class CodeCleaner:
    """
    负责清理Python源代码，移除注释、空行和多余的空白。
    """
    def clean(self, source_code: str) -> str:
        """
        接收源代码字符串，返回清理后的版本。
        """
        tokens = tokenize.generate_tokens(StringIO(source_code).readline)
        cleaned_tokens = []
        for tok_type, tok_val, _, _, _ in tokens:
            # 忽略所有注释和编码声明，保留所有其他类型的token
            if tok_type in (tokenize.COMMENT, tokenize.ENCODING):
                continue
            cleaned_tokens.append((tok_type, tok_val))

        # 将清理后的tokens还原为代码字符串，并移除空行
        cleaned_code = tokenize.untokenize(cleaned_tokens)
        lines = cleaned_code.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        
        return "\n".join(non_empty_lines)
    
class Tokenizer:
    """
    负责将源代码字符串转换为Token序列。
    """
    def tokenize(self, source_code: str) -> List[tokenize.TokenInfo]:
        """
        接收源代码字符串，返回一个过滤后的TokenInfo对象列表。
        """
        try:
            tokens = list(tokenize.generate_tokens(StringIO(source_code).readline))
        except tokenize.TokenError:
            # 如果代码有语法错误，可能会导致Tokenize失败，返回空列表
            return []
            
        # 过滤掉我们不关心的Token类型
        filtered_tokens = []
        for token in tokens:
            # 忽略：文件编码, 换行符, 空的缩进/取消缩进, 文件结束符
            if token.type in (tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE, 
                               tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER,
                               tokenize.COMMENT): # 双重保险，再次忽略注释
                continue
            
            # 忽略只包含空白的字符串TOKEN (通常是多余的空格)
            if token.type == tokenize.STRING and not token.string.strip():
                continue
            
            filtered_tokens.append(token)
            
        return filtered_tokens