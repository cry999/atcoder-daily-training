# >>> atcoder-stat >>>
# started_at  = 2026-09-28T09:14:56+09:00
# solved_at   = 2026-09-28T09:18:40+09:00
# duration_ms = 224207
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, L = map(int, input().split())
ans = 0
for _ in range(N):
    a, b = input().split()
    a = int(a)
    if b == "E":
        ans = max(ans, L - a)
    else:
        ans = max(ans, a)

print(ans)
