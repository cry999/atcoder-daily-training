K = int(input())
MOD = 998244353

ans = 0
for a in range(2, K - 3):
    # b == c == 2 までいけるので 2 <= a <= K-4
    for b in range(2, K - a - 1):
        # c == 2 までいけるので 2 <= b <= K-a-2
        c = K - a - b
        f = K - max(a, b, c)
        ans += f * (a - 1) * (b - 1) * (c - 1)
        ans %= MOD

print(ans)
