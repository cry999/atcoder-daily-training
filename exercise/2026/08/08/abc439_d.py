# >>> atcoder-stat >>>
# started_at  = 2026-08-08T07:33:24+09:00
# solved_at   = 2026-08-08T07:37:32+09:00
# duration_ms = 248376
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

# max(i, j, k) = j となる場合を調査
pre = {}
for a in A:
    if a % 5 == 0:
        b = a // 5 * 7
        c = a // 5 * 3

        ans += pre.get(b, 0) * pre.get(c, 0)

    pre[a] = pre.get(a, 0) + 1

# min(i, j, k) = j となる場合を調査
pre = {}
for a in reversed(A):
    if a % 5 == 0:
        b = a // 5 * 7
        c = a // 5 * 3

        ans += pre.get(b, 0) * pre.get(c, 0)

    pre[a] = pre.get(a, 0) + 1

print(ans)
