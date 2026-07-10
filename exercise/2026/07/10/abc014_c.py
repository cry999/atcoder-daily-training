# >>> atcoder-stat >>>
# started_at  = 2026-07-10T14:25:32+09:00
# solved_at   = 2026-07-10T14:28:43+09:00
# duration_ms = 191475
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())

M = 10**6
C = [0] * (M + 2)

for _ in range(N):
    a, b = map(int, input().split())
    C[a] += 1
    C[b + 1] -= 1

ans = 0
for i in range(M + 1):
    C[i + 1] += C[i]
    ans = max(ans, C[i])
print(ans)
