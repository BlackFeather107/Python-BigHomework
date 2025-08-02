def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    """计算阶乘"""
    if n <= 1:
        return 1
    return n * factorial(n-1)

def is_prime(num):
    """判断是否为质数"""
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True
