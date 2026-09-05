# >>> atcoder-stat >>>
# started_at  = 2026-09-05T11:56:17+09:00
# solved_at   = 2026-09-05T12:00:33+09:00
# duration_ms = 256225
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

sections = [tuple(map(int, input().split())) for _ in range(N)]
sections.sort()

l0, r0 = sections[0]
for l1, r1 in sections:
    if l1 <= r0:
        # 交差している
        l0 = min(l0, l1)
        r0 = max(r0, r1)
    else:
        # 交差していない
        print(l0, r0)
        l0, r0 = l1, r1
print(l0, r0)
