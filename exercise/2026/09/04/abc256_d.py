# >>> atcoder-stat >>>
# started_at  = 2026-09-04T07:31:31+09:00
# solved_at   = 2026-09-04T07:44:14+09:00
# duration_ms = 763771
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


N = int(input())
sections = [tuple(map(int, input().split())) for _ in range(N)]
sections.sort()

l, r = sections[0]
ans = []
for i in range(1, N):
    li, ri = sections[i]
    if li <= r:
        # 交差している。
        # r <= ri は保証されているので考えない
        l = min(l, li)
        r = max(r, ri)
    else:
        # 交差していない
        ans.append((l, r))
        l, r = li, ri

ans.append((l, r))

for l, r in ans:
    print(l, r)
