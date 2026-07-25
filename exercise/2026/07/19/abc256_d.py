# >>> atcoder-stat >>>
# started_at  = 2026-07-19T16:37:04+09:00
# solved_at   = 2026-07-19T16:49:29+09:00
# duration_ms = 745976
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline

N = int(input())
sections = [tuple(map(int, input().split())) for _ in range(N)]
# R の小さい順にソートする
sections.sort(key=lambda x: x[1])

ans = []
for l, r in sections:
    while ans and l <= ans[-1][1]:
        l0, r0 = ans.pop()
        l = min(l, l0)

    ans.append((l, r))

for l, r in ans:
    print(l, r)
