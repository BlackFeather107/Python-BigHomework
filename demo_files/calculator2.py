def add(x, y):
    """加法运算"""
    return x + y

def subtract(x, y):
    """减法运算"""
    return x - y

def multiply(x, y):
    """乘法运算"""
    return x * y

def divide(x, y):
    """除法运算"""
    if y == 0:
        raise ValueError("除数不能为零")
    return x / y

def power(base, exponent):
    """幂运算"""
    return base ** exponent
