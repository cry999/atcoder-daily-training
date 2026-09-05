# >>> atcoder-stat >>>
# started_at  = 2026-09-05T05:38:44+09:00
# solved_at   = 2026-09-05T06:01:11+09:00
# duration_ms = 1347713
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N, Q = map(int, input().split())
(*X,) = map(int, input().split())

prefix = [0] * (Q + 1)
in_set = [False] * (N + 1)
start = [0] * (N + 1)
ans = [0] * (N + 1)

set_size = 0
for i, x in enumerate(X):
    if in_set[x]:
        set_size -= 1
        ans[x] += prefix[i] - prefix[start[x]]
    else:
        set_size += 1
        start[x] = i

    prefix[i + 1] = prefix[i] + set_size
    in_set[x] = not in_set[x]

for x in range(1, N + 1):
    if in_set[x]:
        ans[x] += prefix[Q] - prefix[start[x]]


print(*ans[1:])
