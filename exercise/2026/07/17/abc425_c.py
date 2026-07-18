# >>> atcoder-stat >>>
# started_at  = 2026-07-17T18:52:11+09:00
# solved_at   = 2026-07-17T18:55:31+09:00
# duration_ms = 200384
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, Q = map(int, input().split())
(*A,) = map(int, input().split())

cum = [0] * (2 * N + 1)
for i in range(2 * N):
    cum[i + 1] = cum[i] + A[i % N]


head = 0
for _ in range(Q):
    q, *args = map(int, input().split())
    if q == 1:
        c = args[0]
        head = (head + c) % N
    else:  # q == 2
        l, r = args
        print(cum[r + head] - cum[l + head - 1])
