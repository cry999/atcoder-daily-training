N, W = map(int, input().split())

MAX_V = 10**4
INF = 10**18
# dp[v] := v を達成するための最小の重さ
dp = [INF] * (MAX_V + 1)
dp[0] = 0

for _ in range(N):
    v, w = map(int, input().split())
    for vv in range(MAX_V, v - 1, -1):
        dp[vv] = min(dp[vv], dp[vv - v] + w)

ans = 0
for v in range(MAX_V + 1):
    if dp[v] <= W:
        ans = max(ans, v)
print(ans)
