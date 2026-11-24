# >>> atcoder-stat >>>
# started_at  = 2026-11-24T10:09:38+09:00
# solved_at   = 2026-11-24T10:11:53+09:00
# duration_ms = 135720
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*A,) = map(int, input().split())

j = 0
for i in range(1, N + 1):
    print(A[j] - i)
    if A[j] == i:
        j += 1
