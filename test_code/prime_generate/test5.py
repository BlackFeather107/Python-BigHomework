# prime_5.py
# 完全不同思路的非抄袭代码：埃拉托斯特尼筛法 (Sieve of Eratosthenes)

def sieve_for_primes(limit):
    """使用筛法找出小于limit的所有素数。"""
    # 创建一个从0到limit的布尔列表，初始都为True
    primes_bool = [True] * (limit + 1)
    if limit >= 0:
        primes_bool[0] = False
    if limit >= 1:
        primes_bool[1] = False
    
    # 从第一个素数2开始
    for number in range(2, int(limit**0.5) + 1):
        if primes_bool[number]:
            # 将该素数的所有倍数标记为非素数
            for multiple in range(number*number, limit + 1, number):
                primes_bool[multiple] = False
                
    # 收集所有标记为True的数字
    prime_numbers = []
    for number in range(limit + 1):
        if primes_bool[number]:
            prime_numbers.append(number)
    return prime_numbers

if __name__ == "__main__":
    # 为了找到前100个素数，我们需要一个大致的上限
    # 根据素数定理，第n个素数约等于 n*ln(n)
    # 100 * ln(100) approx 100 * 4.6 = 460. 我们设置一个更安全的上限，比如600
    upper_limit = 600 
    all_primes_found = sieve_for_primes(upper_limit)
    
    # 从找到的所有素数中，取前100个
    first_100_primes = all_primes_found[:100]
    
    print("使用筛法找到的前100个素数是:")
    print(first_100_primes)