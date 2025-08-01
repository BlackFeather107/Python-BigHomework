# prime_3.py
# 调整了函数定义顺序的代码

def find_first_100_primes():
    """找到并返回前100个素数。"""
    primes_found = []
    num = 2
    while len(primes_found) < 100:
        # 函数 is_prime 在后面定义，但在Python中这是合法的
        if is_prime(num):
            primes_found.append(num)
        num += 1
    return primes_found

def is_prime(n):
    """检查一个数字是否为素数。"""
    if n <= 1:
        return False
    # 只需检查到 n 的平方根
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    # 主程序入口
    prime_list = find_first_100_primes()
    print("前100个素数是:")
    print(prime_list)