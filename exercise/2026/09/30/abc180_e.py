# >>> atcoder-stat >>>
# started_at  = 2026-09-30T09:34:10+09:00
# solved_at   = 2026-09-30T09:51:29+09:00
# duration_ms = 1039636
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())

pos = [tuple(map(int, input().split())) for _ in range(N)]

INF = 10**18
# dp[S][i] := 訪れた頂点集合が S で、最後に訪れた街が i である時の最小コスト
dp = [[INF] * N for _ in range(1 << N)]
dp[1][0] = 0

for s in range(1 << N):
    for src in range(N):  # 起点となる街
        if s & (1 << src) == 0:
            # 起点となる街は訪れていないとダメ。
            continue
        a, b, c = pos[src]
        for dst in range(N):  # 行き先となる街
            if src == dst:
                # 同じ街だけは意味ないのでスキップ
                continue
            # 訪問回数に上限はないので、訪問済みでもいい。
            p, q, r = pos[dst]

            cost = abs(p - a) + abs(q - b) + max(0, r - c)

            ns = s | (1 << dst)
            dp[ns][dst] = min(dp[ns][dst], dp[s][src] + cost)
print(dp[-1][0])
