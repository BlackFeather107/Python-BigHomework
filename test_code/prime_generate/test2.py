# prime_2.py
# 几乎完全抄袭的代码，只增加了一行注释

def is_prime(n):
    """检查一个数字是否为素数。"""
    if n <= 1:
        return False
    # 只需检查到 n 的平方根
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def find_first_100_primes():
    """找到并返回前100个素数。"""
    # 这是一个简单的计数循环
    primes_found = []
    num = 2
    while len(primes_found) < 100:
        if is_prime(num):
            primes_found.append(num)
        num += 1
    return primes_found

if __name__ == "__main__":
    prime_list = find_first_100_primes()
    print("前100个素数是:")
    print(prime_list)