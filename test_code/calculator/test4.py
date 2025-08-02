# test4.py
# 抄袭test1，大幅替换命名和顺序，并添加无意义代码

import re

# 一个无用的全局变量
IS_LOGGING_ENABLED = False

def log(message):
    """一个不会被调用的日志函数"""
    if IS_LOGGING_ENABLED:
        print(f"[LOG] {message}")

def compute_rpn(rpn_list):
    """计算逆波兰式"""
    calc_stack = []
    for item in rpn_list:
        if isinstance(item, int):
            calc_stack.append(item)
        else:
            # 增加无意义的日志调用
            log(f"执行操作: {item}")
            op2 = calc_stack.pop()
            op1 = calc_stack.pop()
            if item == '+':
                calc_stack.append(op1 + op2)
            elif item == '-':
                calc_stack.append(op1 - op2)
            elif item == '*':
                calc_stack.append(op1 * op2)
            elif item == '/':
                calc_stack.append(op1 / op2)
    return calc_stack[0]

def create_rpn_from_infix(formula):
    """从中缀式生成逆波兰式"""
    levels = {'+': 1, '-': 1, '*': 2, '/': 2}
    val_queue = []
    op_stack = []
    parts = re.findall(r'(\d+|\S)', formula)
    for p in parts:
        if p.isdigit():
            val_queue.append(int(p))
        elif p in levels:
            while (op_stack and op_stack[-1] != '(' and
                   levels.get(op_stack[-1], 0) >= levels.get(p, 0)):
                val_queue.append(op_stack.pop())
            op_stack.append(p)
        elif p == '(':
            op_stack.append(p)
        elif p == ')':
            while op_stack and op_stack[-1] != '(':
                val_queue.append(op_stack.pop())
            if op_stack and op_stack[-1] == '(':
                op_stack.pop()
    while op_stack:
        val_queue.append(op_stack.pop())
    return val_queue

if __name__ == "__main__":
    input_str = "10 + (2 * 6) - (10 / 5)"
    rpn = create_rpn_from_infix(input_str)
    final_answer = compute_rpn(rpn)
    print(f"计算: '{input_str}' = {final_answer}")