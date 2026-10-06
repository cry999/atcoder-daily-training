# >>> atcoder-stat >>>
# started_at  = 2026-10-02T12:26:11+09:00
# solved_at   = 2026-10-02T13:29:13+09:00
# duration_ms = 3782690
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
N, X = map(int, input().split())
(*Y,) = map(int, input().split())  # 壁 [i] の位置
(*Z,) = map(int, input().split())  # 壁 [i] を壊せるハンマーの位置


events = sorted([0, X, *Y, *Z])
required_hammer = dict(zip(Y, Z))

start = events.index(0)
goal = events.index(X)

M = len(events)

INF = 10**18
dp = [[[INF] * 2 for _ in range(M)] for _ in range(M)]
dp[start][start][0] = 0
dp[start][start][1] = 0

ans = INF
for d in range(M):
    for l in range(M - d):
        r = l + d
        l_pos, r_pos = events[l], events[r]
        l_val, r_val = dp[l][r]

        if l == goal:
            ans = min(ans, l_val)
        if r == goal:
            ans = min(ans, r_val)

        if l - 1 >= 0:
            x = events[l - 1]
            if x not in required_hammer or l_pos <= required_hammer[x] <= r_pos:
                dp[l - 1][r][0] = min(
                    dp[l - 1][r][0],
                    l_val + l_pos - x,
                    r_val + r_pos - x,
                )

        if r + 1 < M:
            x = events[r + 1]
            if x not in required_hammer or l_pos <= required_hammer[x] <= r_pos:
                dp[l][r + 1][1] = min(
                    dp[l][r + 1][1],
                    l_val + x - l_pos,
                    r_val + x - r_pos,
                )

print(ans if ans != INF else -1)
