# >>> atcoder-stat >>>
# started_at  = 2026-10-03T13:04:57+09:00
# solved_at   = 2026-10-03T13:35:04+09:00
# duration_ms = 1807144
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, X = map(int, input().split())
(*Y,) = map(int, input().split())
(*Z,) = map(int, input().split())

# 考察
# 1. 各位置で起きるイベントを考える。
# 2. dp[l][r][l/r] := 区間 [l, r] のイベントが起きて、l or r にいる時の最小移動距離
# 3. こうすると、min(dp[l][goal][right] for l in range(goal)) か min(dp[goal][r][left] for r in range(goal + 1, E)) が答え
# 4. 壁の位置に移動する場合は、対応するハンマーのイベントをクリアしていることを確認する必要がある
# 5. したがって、壁の位置からハンマーの位置を逆算できるようにする必要がある。

events = sorted([0, X, *Y, *Z])
start = events.index(0)
goal = events.index(X)


M = len(events)
INF = 10**18

hammer_pos = {}
j = 0
for i in sorted(range(N), key=lambda i: Z[i]):
    while j < M and events[j] != Z[i]:
        j += 1
    hammer_pos[Y[i]] = j

dp = [[[INF] * 2 for _ in range(M)] for _ in range(M)]
dp[start][start][:] = 0, 0

L, R = 0, 1

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
            if x not in hammer_pos or l <= hammer_pos[x] <= r:
                dp[l - 1][r][L] = min(
                    dp[l - 1][r][L],
                    l_val + l_pos - x,
                    r_val + r_pos - x,
                )
        if r + 1 < M:
            x = events[r + 1]
            if x not in hammer_pos or l <= hammer_pos[x] <= r:
                dp[l][r + 1][R] = min(
                    dp[l][r + 1][R],
                    l_val + x - l_pos,
                    r_val + x - r_pos,
                )
print(f"[DEBUG] {dp=}")
if ans == INF:
    print(-1)
else:
    print(ans)
