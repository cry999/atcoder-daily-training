N, W = map(int, input().split())
wv = [tuple(map(int, input().split())) for _ in range(N)]
V = sum(v for _, v in wv)
dp = [float("inf")] * (V + 1)
dp[0] = 0

for w, v in wv:
    for vv in range(V, -1, -1):
        dp[vv] = min(dp[vv], dp[vv - v] + w if vv - v >= 0 else float("inf"))
v = 0
for vv in range(V + 1):
    if dp[vv] <= W:
        v = vv
print(v)
