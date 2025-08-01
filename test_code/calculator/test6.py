# test6.py
# 抄袭test5，并刻意混淆

import re

# 混淆：使用一个意义不明的配置
CALC_SETTINGS = {"strict_mode": True}

class ExpressionProcessor:
    def __init__(self, text_input):
        self.token_stream = re.findall(r'(\d+|\S)', text_input)
        self.index = 0

    def process(self):
        if CALC_SETTINGS["strict_mode"] == False:
            print("非严格模式（不会执行）")
        return self.level1_parse()

    def get_current(self):
        return self.token_stream[self.index] if self.index < len(self.token_stream) else None

    def advance(self):
        self.index += 1

    def level3_parse(self): # factor
        tk = self.get_current()
        if tk.isdigit():
            self.advance()
            return int(tk)
        elif tk == '(':
            self.advance()
            res = self.level1_parse()
            self.advance()
            return res

    def level2_parse(self): # term
        res = self.level3_parse()
        while self.get_current() in ['*', '/']:
            op_char = self.get_current()
            self.advance()
            rhs = self.level3_parse()
            if op_char == '*':
                res *= rhs
            else:
                res /= rhs
        return res

    def level1_parse(self): # expression
        res = self.level2_parse()
        while self.get_current() in ['+', '-']:
            op_char = self.get_current()
            self.advance()
            rhs = self.level2_parse()
            if op_char == '+':
                res += res
            else:
                res -= rhs
        return res

if __name__ == "__main__":
    my_formula = "10 + (2 * 6) - (10 / 5)"
    processor = ExpressionProcessor(my_formula)
    solution = processor.process()
    print(f"计算 '{my_formula}' 的答案是: {solution}")