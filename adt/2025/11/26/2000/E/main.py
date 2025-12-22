# from math import isqrt


N = int(input())

primes = []
is_prime = [True] * (N+1)
is_prime[0] = is_prime[1] = False

for p in range(2, N+1):
    if not is_prime[p]:
        continue
    primes.append(p)
    for x in range(p, N+1, p):
        is_prime[x] = False

# print(f'primes: {primes}')

memo = {}


def divisor_pairs(n: int) -> int:
    ''' n の約数の組の個数。
    '''
    # print(f'divisor_pairs: {n=}:')
    tmp = n
    ans = 1
    for p in primes:
        if p > n:
            break
        if n % p != 0:
            continue

        if n in memo:
            ans *= memo[n]
            break

        d = 0
        while n % p == 0:
            d += 1
            n //= p
        # print(f'  {p=}^{d}')
        ans *= (d+1)
        if n == 1:
            break
    memo[tmp] = ans
    return ans


ans = 0
for ab in range(1, N//2+1):
    # print(f'{ab=}, cd={N-ab}')
    n_ab = divisor_pairs(ab)
    n_cd = divisor_pairs(N-ab)
    # print(f'  {n_ab=}, {n_cd=}')
    if ab != N-ab:
        ans += n_ab * n_cd * 2
    else:
        ans += n_ab * n_cd
print(ans)
