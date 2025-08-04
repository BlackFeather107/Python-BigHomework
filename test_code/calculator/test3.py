# test3.py
# 抄袭test1，替换前后顺序
import re

def evaluate_postfix(postfix_tokens):
    """计算后缀表达式的函数"""
    eval_stack = []
    for token in postfix_tokens:
        if isinstance(token, int):
            eval_stack.append(token)
        else:
            val2 = eval_stack.pop()
            val1 = eval_stack.pop()
            if token == '+':
                eval_stack.append(val1 + val2)
            elif token == '-':
                eval_stack.append(val1 - val2)
            elif token == '*':
                eval_stack.append(val1 * val2)
            elif token == '/':
                eval_stack.append(val1 / val2)
    return eval_stack[0]

def convert_to_postfix(expression):
    """将中缀表达式转为后缀的函数"""
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    output_queue = []
    operator_stack = []
    tokens = re.findall(r'(\d+|\S)', expression)
    for token in tokens:
        if token.isdigit():
            output_queue.append(int(token))
        elif token in precedence:
            while (operator_stack and operator_stack[-1] != '(' and
                   precedence.get(operator_stack[-1], 0) >= precedence.get(token, 0)):
                output_queue.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                output_queue.append(operator_stack.pop())
            if operator_stack and operator_stack[-1] == '(':
                operator_stack.pop()
    while operator_stack:
        output_queue.append(operator_stack.pop())
    return output_queue

if __name__ == "__main__":
    math_expr = "10 + (2 * 6) - (10 / 5)"
    postfix_form = convert_to_postfix(math_expr)
    result = evaluate_postfix(postfix_form)
    print(f"The result of '{math_expr}' is: {result}")