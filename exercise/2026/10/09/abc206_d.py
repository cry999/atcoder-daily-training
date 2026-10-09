# >>> atcoder-stat >>>
# started_at  = 2026-10-09T08:38:22+09:00
# solved_at   = 2026-10-09T08:42:26+09:00
# duration_ms = 244175
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.dsu import DSU

N = int(input())
(*A,) = map(int, input().split())

dsu = DSU(max(A) + 1)
ans = 0
for i in range(N // 2):
    x = dsu.leader(A[i])
    y = dsu.leader(A[N - 1 - i])

    if x == y:
        continue
    dsu.merge(x, y)
    ans += 1

print(ans)
