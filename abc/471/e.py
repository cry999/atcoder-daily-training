MOD = 998244353

N, K = map(int, input().split())
(*A,) = map(int, input().split())


def comb(n: int, r: int):
    r = min(r, n - r)
    c = 1
    for i in range(1, r + 1):
        c = c * (n - r + i) % MOD
        c = c * pow(i, MOD - 2, MOD) % MOD
    return c


co1 = comb(N - 1, K - 1)
co2 = co1 * (K - 1) * pow(N - 1, MOD - 2, MOD) % MOD

ans = 0
for a in A:
    ans += co1 * a * a % MOD
    ans %= MOD

s = sum(A) % MOD
for a in A:
    s -= a
    s %= MOD

    ans += 2 * co2 * a * s % MOD
    ans %= MOD

print(ans)
