# test1.py
# 基准代码：使用Shunting-yard算法实现，思路与C代码最接近

import re

def shunting_yard_calculator(expression):
    """使用Shunting-yard算法计算中缀表达式"""
    
    # 定义操作符优先级
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    output_queue = []
    operator_stack = []

    # 使用正则表达式分割表达式为数字和操作符
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

    # 计算后缀表达式
    eval_stack = []
    for token in output_queue:
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

if __name__ == "__main__":
    math_expr = "10 + (2 * 6) - (10 / 5)"
    result = shunting_yard_calculator(math_expr)
    print(f"'{math_expr}' 的计算结果是: {result}")