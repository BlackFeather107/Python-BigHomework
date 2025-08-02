# test2.py
# 抄袭test1，大幅替换命名

import re

def rpn_engine(formula):
    """通过逆波兰表示法引擎处理算式"""
    
    op_level = {'+': 1, '-': 1, '*': 2, '/': 2}

    value_list = []
    op_holder = []

    parts = re.findall(r'(\d+|\S)', formula)

    for part in parts:
        if part.isdigit():
            value_list.append(int(part))
        elif part in op_level:
            while (op_holder and op_holder[-1] != '(' and
                   op_level.get(op_holder[-1], 0) >= op_level.get(part, 0)):
                value_list.append(op_holder.pop())
            op_holder.append(part)
        elif part == '(':
            op_holder.append(part)
        elif part == ')':
            while op_holder and op_holder[-1] != '(':
                value_list.append(op_holder.pop())
            if op_holder and op_holder[-1] == '(':
                op_holder.pop()

    while op_holder:
        value_list.append(op_holder.pop())

    compute_stack = []
    for item in value_list:
        if isinstance(item, int):
            compute_stack.append(item)
        else:
            operand_2 = compute_stack.pop()
            operand_1 = compute_stack.pop()
            if item == '+':
                compute_stack.append(operand_1 + operand_2)
            elif item == '-':
                compute_stack.append(operand_1 - operand_2)
            elif item == '*':
                compute_stack.append(operand_1 * operand_2)
            elif item == '/':
                compute_stack.append(operand_1 / operand_2)
    
    return compute_stack[0]

if __name__ == "__main__":
    expression_str = "10 + (2 * 6) - (10 / 5)"
    final_value = rpn_engine(expression_str)
    print(f"表达式 '{expression_str}' 的值是: {final_value}")