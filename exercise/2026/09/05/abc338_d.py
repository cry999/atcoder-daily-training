# >>> atcoder-stat >>>
# started_at  = 2026-09-05T12:43:00+09:00
# solved_at   = 2026-09-05T12:47:36+09:00
# duration_ms = 276725
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*X,) = map(int, input().split())

ans = [0] * (N + 1)
for i in range(M - 1):
    x1, x2 = sorted([X[i], X[i + 1]])

    r1 = x2 - x1
    r2 = N - r1

    # x1 - x2 の間の橋を落としたら r2 を通らないといけない
    ans[x1] += r2
    ans[x2] -= r2

    # それ以外の橋を落としたら r1 を通らないといけない
    ans[0] += r1
    ans[x1] -= r1
    ans[x2] += r1

for i in range(N):
    ans[i + 1] += ans[i]

print(min(ans))
