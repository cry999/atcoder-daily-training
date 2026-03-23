N, D = map(int, input().split())
(*A,) = map(int, input().split())


MOD = 998244353

fact = [1] * (N + 1)
fact_inv = [1] * (N + 1)

for i in range(2, N + 1):
    fact[i] = fact[i - 1] * i % MOD

fact_inv[-1] = pow(fact[-1], MOD - 2, MOD)
for i in range(N, 0, -1):
    fact_inv[i - 1] = fact_inv[i] * i % MOD


def comb(n: int, r: int) -> int:
    if n < 0 or r < 0 or n < r:
        return 0
    return (fact[n] * fact_inv[r] % MOD) * fact_inv[n - r] % MOD


cnt = {}
for a in A:
    cnt[a] = cnt.get(a, 0) + 1

ans = 1
s = 0
for i in range(max(A) + 1):
    s += cnt.get(i, 0)
    ans *= comb(s, cnt.get(i, 0))
    ans %= MOD
    if i >= D:
        s -= cnt.get(i - D, 0)

print(ans)
