N, W = map(int, input().split())
wv = [tuple(map(int, input().split())) for _ in range(N)]

sum_v = sum(v for _, v in wv)

dp = [float("inf")] * (sum_v + 1)
dp[0] = 0

for w, v in wv:
    for vv in range(sum_v, v - 1, -1):
        dp[vv] = min(dp[vv], dp[vv - v] + w)

v = 0
for vv, ww in enumerate(dp):
    if ww <= W:
        v = vv
print(v)
