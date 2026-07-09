m, n = map(int, input().split())
MOD = 10**9 + 7

ans = 1
while n > 0:
    if n & 1:
        ans *= m
        ans %= MOD
    m = (m * m) % MOD
    n >>= 1
print(ans)
