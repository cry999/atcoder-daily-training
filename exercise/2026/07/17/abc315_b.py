# >>> atcoder-stat >>>
# started_at  = 2026-07-17T18:42:03+09:00
# solved_at   = 2026-07-17T18:44:55+09:00
# duration_ms = 172219
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
M = int(input())
(*D,) = map(int, input().split())

mid = (sum(D) + 1) // 2

s = 0
for i in range(M):
    if s + D[i] == mid:
        print(i + 1, D[i])
    elif s + D[i] > mid:
        print(i + 1, mid - s)
    else:
        s += D[i]
        continue
    break
