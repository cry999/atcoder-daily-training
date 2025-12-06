N = int(input())
MOD = 998244353


def digit(n: int) -> int:
    d = 0
    while n:
        d += 1
        n //= 10
    return d


def f(n: int) -> int:
    dn = digit(n)
    ans = pow(10**dn, n, mod=MOD)-1
    ans *= pow(10**dn - 1, MOD-2, mod=MOD)
    ans %= MOD
    ans *= n
    return ans % MOD


print(f(N))
