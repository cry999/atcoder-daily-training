# >>> atcoder-stat >>>
# started_at  = 2026-07-17T18:37:45+09:00
# solved_at   = 2026-07-17T18:41:04+09:00
# duration_ms = 199357
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
S = [input() for _ in range(N)]
T = [input() for _ in range(M)]

D = N - M + 1
for p in range(D * D):
    i, j = divmod(p, D)
    for d in range(M * M):
        di, dj = divmod(d, M)
        if S[i + di][j + dj] != T[di][dj]:
            break
    else:
        print(i + 1, j + 1)
