MOD = 998244353
N, M = map(int, input().split())

ans = 0
pow2 = 2
while M:
    if M & 1:
        ans += (pow2 // 2) * (N // pow2)
        ans += max(N % pow2 - pow2 // 2 + 1, 0)
        ans %= MOD
    pow2 <<= 1
    M >>= 1
print(ans)
