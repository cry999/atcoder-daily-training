# >>> atcoder-stat >>>
# started_at  = 2026-07-22T17:23:32+09:00
# solved_at   = 2026-07-22T17:27:27+09:00
# duration_ms = 235898
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())

ans = 0
prefix = {}

for a in A:
    prefix[a] = prefix.get(a - 1, 0) + 1
    ans = max(ans, prefix[a])

print(ans)
