MOD = 10**9 + 7
n, r = map(int, input().split())

a, b = 1, 1
for i in range(1, n+1):
    if i <= r:
        b = (b * i) % MOD
    if i <= n - r:
        b = (b * i) % MOD
    a = (a * i) % MOD


def mod_pow(a: int, b: int, m: int) -> int:
    p = 1
    while b:
        if b & 1:
            p = (p * a) % m
        a = (a * a) % m
        b >>= 1
    return p


print((a * mod_pow(b, MOD - 2, MOD)) % MOD)
