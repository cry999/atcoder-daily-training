N = int(input())
(*T,) = map(int, input().split())

M = sum(T)
dp = [False] * (M + 1)
dp[0] = True

for i, t in enumerate(T):
    for x in range(M, -1, -1):
        if dp[x] and x + t <= M:
            dp[x + t] = True

ans = M
for x in range((M + 1) // 2 + 1):
    if dp[x]:
        ans = min(ans, max(x, M - x))

print(ans)
