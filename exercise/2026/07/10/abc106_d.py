# >>> atcoder-stat >>>
# started_at  = 2026-07-10T13:54:58+09:00
# solved_at   = 2026-07-10T14:09:56+09:00
# duration_ms = 898338
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N, M, Q = map(int, input().split())
C = [[0] * (N + 1) for _ in range(N + 1)]
for _ in range(M):
    l, r = map(int, input().split())
    C[1][r] += 1
    if l + 1 <= N:
        C[l + 1][r] -= 1

for i in range(N):
    for j in range(N + 1):
        C[i + 1][j] += C[i][j]
for i in range(N + 1):
    for j in range(N):
        C[i][j + 1] += C[i][j]

for _ in range(Q):
    p, q = map(int, input().split())
    print(C[p][q])
