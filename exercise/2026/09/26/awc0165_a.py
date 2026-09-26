# >>> atcoder-stat >>>
# started_at  = 2026-09-26T16:58:57+09:00
# solved_at   = 2026-09-26T17:04:34+09:00
# duration_ms = 337118
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, Q = map(int, input().split())
(*A,) = map(int, input().split())  # N
(*B,) = map(int, input().split())  # N
(*C,) = map(int, input().split())  # Q

for i in range(Q):
    c = C[i] - 1
    falldown = max(0, A[c] - B[c])
    A[c] = 0
    if c + 1 < N:
        A[c + 1] += falldown

print(*A)
