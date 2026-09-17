# >>> atcoder-stat >>>
# started_at  = 2026-09-16T01:23:14+09:00
# solved_at   = 2026-09-16T01:27:37+09:00
# duration_ms = 263371
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
takahashi, aoki = 0, 0
diff = []

for _ in range(N):
    a, b = map(int, input().split())
    aoki += a
    diff.append(2 * a + b)

diff.sort()

ans = 0
while aoki >= takahashi:
    takahashi += diff.pop()
    ans += 1
print(ans)
