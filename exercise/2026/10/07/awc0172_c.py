# >>> atcoder-stat >>>
# started_at  = 2026-10-07T06:56:49+09:00
# solved_at   = 2026-10-07T06:59:37+09:00
# duration_ms = 168117
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*W,) = map(int, input().split())

ans = [False] * N
for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    if W[u] < W[v]:
        ans[u] = True
    if W[u] > W[v]:
        ans[v] = True

print(sum(ans))
