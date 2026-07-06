# >>> atcoder-stat >>>
# started_at  = 2026-07-06T16:14:57+09:00
# solved_at   = 2026-07-06T16:29:00+09:00
# duration_ms = 843630
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<


n, m = map(int, input().split())
relationships = [[False] * n for _ in range(n)]
for _ in range(m):
    x, y = map(int, input().split())
    relationships[x - 1][y - 1] = True
    relationships[y - 1][x - 1] = True

ans = 0
for bit in range(1, 1 << n):
    members = [i for i in range(n) if bit & (1 << i)]
    num = bit.bit_count()

    ok = True
    for i1 in range(num):
        m1 = members[i1]
        for i2 in range(num):
            if i1 == i2:
                continue
            m2 = members[i2]
            if not relationships[m1][m2]:
                ok = False
                break
    if ok:
        ans = max(ans, num)
print(ans)
