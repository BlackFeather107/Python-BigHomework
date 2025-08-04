# prime_4.py
# 调整了变量和函数名的代码

def check_if_prime_number(number):
    """验证一个整数是否为质数。"""
    if number <= 1:
        return False
    # 循环检查因子
    for factor in range(2, int(number**0.5) + 1):
        if number % factor == 0:
            return False
    return True

def get_top_100_primes():
    """获取并返回前100个质数。"""
    collected_primes = []
    candidate_number = 2
    while len(collected_primes) < 100:
        if check_if_prime_number(candidate_number):
            collected_primes.append(candidate_number)
        candidate_number += 1
    return collected_primes

if __name__ == "__main__":
    list_of_primes = get_top_100_primes()
    print("The first 100 prime numbers are:")
    print(list_of_primes)
