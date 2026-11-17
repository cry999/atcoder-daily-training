# >>> atcoder-stat >>>
# started_at  = 2026-11-15T12:32:36+09:00
# solved_at   = 2026-11-15T14:19:28+09:00
# duration_ms = 6412914
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
(*A,) = map(int, input().split())


prev, n = -1, 0
freq = [0] * (N + 1)

ans = 1
for a in A:
    freq[a] += 1
    n += 1
    if a == prev:
        continue
    ans += n - freq[a]
    prev = a
print(ans)
