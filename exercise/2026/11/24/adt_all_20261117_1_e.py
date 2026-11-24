# >>> atcoder-stat >>>
# started_at  = 2026-11-24T13:12:00+09:00
# solved_at   = 2026-11-24T13:27:38+09:00
# duration_ms = 938395
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, K, X = map(int, input().split())
(*A,) = map(int, input().split())
A.sort(reverse=True)

s = 0
for i in range(N - K, N):
    s += A[i]
    if s >= X:
        print(i + 1)
        break
else:
    print(-1)
