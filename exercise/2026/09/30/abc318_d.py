# >>> atcoder-stat >>>
# started_at  = 2026-09-30T09:26:37+09:00
# solved_at   = 2026-09-30T09:33:57+09:00
# duration_ms = 440566
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
D = [list(map(int, input().split())) for _ in range(N - 1)]

# dp[S] := 頂点集合 S がすでに使用済みの頂点の集合とした時の、選んだ変の重みの総和の最大値
dp = [0] * (1 << N)

for s in range(1 << N):
    for i in range(N):
        if s & (1 << i):
            # visited
            continue
        for j in range(i + 1, N):
            if s & (1 << j):
                # visited
                continue

            # 辺 (i, j) を新たに追加する。
            ns = s | (1 << i) | (1 << j)
            dp[ns] = max(dp[ns], dp[s] + D[i][j - i - 1])

print(dp[-1])
