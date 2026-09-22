# >>> atcoder-stat >>>
# started_at  = 2026-09-21T10:13:21+09:00
# solved_at   = 2026-09-21T10:21:00+09:00
# duration_ms = 459674
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
from collections import deque

input = sys.stdin.readline


N = int(input())
(*A,) = map(int, input().split())

# last_q1 := 最後に出たクエリ 1 の (index, value)
last_q1 = (-1, 0)

# q2[i] := A[i] に対するクエリ 2 の (index, x)
q2 = [deque() for _ in range(N)]
last = [-1] * N

Q = int(input())
for q in range(Q):
    query, *args = map(int, input().split())

    if query == 1:
        last_q1 = (q, args[0])
    elif query == 2:
        i, x = args
        q2[i - 1].append((q, x))
    else:  # query == 3
        i = args[0] - 1
        while q2[i] and q2[i][0][0] < last_q1[0]:
            q2[i].popleft()

        if last[i] < last_q1[0]:
            last[i], A[i] = last_q1

        while q2[i]:
            last[i], x = q2[i].popleft()
            A[i] += x

        print(A[i])
