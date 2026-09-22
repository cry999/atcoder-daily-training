# >>> atcoder-stat >>>
# started_at  = 2026-09-22T17:49:20+09:00
# solved_at   = 2026-09-22T17:53:29+09:00
# duration_ms = 249226
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

ans = []
for i in range(N):
    if not ans:
        ans.append(list(sections[i]))
    else:
        l0, r0 = ans[-1]
        l1, r1 = sections[i]
        assert l0 <= l1
        if l1 <= r0:
            # 交わっている
            ans[-1][1] = max(r0, r1)
        else:
            # 交わっていない
            ans.append([l1, r1])

for l, r in ans:
    print(l, r)
