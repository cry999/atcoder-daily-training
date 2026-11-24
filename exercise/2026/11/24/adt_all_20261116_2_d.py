# >>> atcoder-stat >>>
# started_at  = 2026-11-24T09:57:59+09:00
# solved_at   = 2026-11-24T10:09:34+09:00
# duration_ms = 695007
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
M = 100
s = [[0] * (M + 1) for _ in range(M + 1)]
for _ in range(N):
    A, B, C, D = map(int, input().split())
    s[B][D] += 1
    s[B][C] -= 1
    s[A][D] -= 1
    s[A][C] += 1

for i in range(M + 1):
    for j in range(M):
        s[i][j + 1] += s[i][j]
for i in range(M):
    for j in range(M + 1):
        s[i + 1][j] += s[i][j]

ans = 0
for i in range(M):
    for j in range(M):
        ans += s[i][j] > 0
print(ans)
