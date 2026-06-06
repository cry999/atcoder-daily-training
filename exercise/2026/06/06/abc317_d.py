N = int(input())
secs = [tuple(map(int, input().split())) for _ in range(N)]

# 総議席数
Z = sum(z for _, _, z in secs)
# dp[z] := z 議席を獲得するための最小移動人数
dp = [float("inf")] * (Z + 1)
dp[0] = 0

for x, y, z in secs:
    move = max(0, (y - x + 1) // 2)
    for i in range(Z - z, -1, -1):
        dp[i + z] = min(dp[i + z], dp[i] + move)

print(min(dp[(Z + 1) // 2 :]))
