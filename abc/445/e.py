from math import isqrt
from sys import stdin

input = stdin.readline


def main():
    T = int(input())
    MOD = 998244353

    primes = []
    max_a = isqrt(10**7)
    is_prime = [True] * (max_a + 1)
    is_prime[0] = is_prime[1] = False

    for p in range(2, max_a + 1):
        if not is_prime[p]:
            continue
        primes.append(p)
        for k in range(2 * p, max_a + 1, p):
            is_prime[k] = False

    for _ in range(T):
        N = int(input())
        (*A,) = map(int, input().split())

        # factos[i] = A[i] の素因数分解
        factors = [{} for _ in range(N)]
        # max_factors: A[0]...A[N-1] での素因数 p の最大指数と 2 番手指数
        max_factors = {}

        for i, a in enumerate(A):
            for p in primes:
                if p * p > a:
                    break
                if a % p:
                    continue
                while a % p == 0:
                    a //= p
                    factors[i][p] = factors[i].get(p, 0) + 1
                if p not in max_factors:
                    max_factors[p] = (0, 0)

                if factors[i][p] > max_factors[p][0]:
                    max_factors[p] = (
                        factors[i][p],
                        max_factors[p][0],
                    )
                elif factors[i][p] > max_factors[p][1]:
                    max_factors[p] = (
                        max_factors[p][0],
                        factors[i][p],
                    )
            if a > 1:
                p = a
                factors[i][p] = 1
                if p not in max_factors:
                    max_factors[p] = (0, 0)
                if factors[i][p] > max_factors[p][0]:
                    max_factors[p] = (
                        factors[i][p],
                        max_factors[p][0],
                    )
                elif factors[i][p] > max_factors[p][1]:
                    max_factors[p] = (
                        max_factors[p][0],
                        factors[i][p],
                    )

        lcm = 1
        for p, (e1, _) in max_factors.items():
            lcm = lcm * pow(p, e1, MOD) % MOD

        ans = []
        for i in range(N):
            n = lcm
            for p, d in factors[i].items():
                if max_factors[p][0] > d:
                    continue
                n *= pow(p, MOD - 1 - (max_factors[p][0] - max_factors[p][1]), MOD)
                n %= MOD
            ans.append(n)

        print(*ans)


main()
