# >>> atcoder-stat >>>
# started_at  = 2026-07-11T09:34:51+09:00
# solved_at   = 2026-07-11T09:36:51+09:00
# duration_ms = 120343
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
A, B, K = map(int, input().split())
takahashi = max(A - K, 0)
K -= A - takahashi
aoki = max(B - K, 0)
print(takahashi, aoki)
