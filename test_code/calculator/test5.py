# test5.py
# 另一种实现思路：递归下降解析器
import re

class CalculatorParser:
    def __init__(self, expression):
        self.tokens = re.findall(r'(\d+|\S)', expression)
        self.pos = 0

    def parse(self):
        return self.parse_expression()

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume_token(self):
        self.pos += 1

    def parse_factor(self):
        token = self.current_token()
        if token.isdigit():
            self.consume_token()
            return int(token)
        elif token == '(':
            self.consume_token()
            result = self.parse_expression()
            self.consume_token()  # Consume ')'
            return result

    def parse_term(self):
        result = self.parse_factor()
        while self.current_token() in ['*', '/']:
            op = self.current_token()
            self.consume_token()
            right = self.parse_factor()
            if op == '*':
                result *= right
            else:
                result /= right
        return result

    def parse_expression(self):
        result = self.parse_term()
        while self.current_token() in ['+', '-']:
            op = self.current_token()
            self.consume_token()
            right = self.parse_term()
            if op == '+':
                result += right
            else:
                result -= right
        return result

if __name__ == "__main__":
    math_expr = "10 + (2 * 6) - (10 / 5)"
    parser = CalculatorParser(math_expr)
    result = parser.parse()
    print(f"'{math_expr}' 的计算结果是: {result}")