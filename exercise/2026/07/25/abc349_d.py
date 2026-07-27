# >>> atcoder-stat >>>
# started_at  = 2026-07-25T20:07:13+09:00
# solved_at   = 2026-07-25T20:15:42+09:00
# duration_ms = 509856
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 2
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
L, R = map(int, input().split())

ans = []
l = L
while l < R:
    pow2 = 1
    while True:
        if l % pow2 != 0:
            pow2 //= 2
            break

        j = l // pow2
        r = pow2 * (j + 1)

        if r > R:
            pow2 //= 2
            break

        pow2 *= 2

    j = l // pow2
    r = pow2 * (j + 1)
    ans.append((l, r))
    l = r

print(len(ans))
for l, r in ans:
    print(l, r)
