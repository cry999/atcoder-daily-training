# >>> atcoder-stat >>>
# started_at  = 2026-09-05T09:16:19+09:00
# solved_at   = 2026-09-05T09:21:14+09:00
# duration_ms = 295686
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
(*A,) = map(int, input().split())

last_reset_time = -1
last_reset_value = 0

last_query = [-1] * N

Q = int(input())
for i in range(Q):
    query, *args = map(int, input().split())

    if query == 1:
        last_reset_time = i
        last_reset_value = args[0]
    elif query == 2:
        j, x = args
        j -= 1
        if last_query[j] < last_reset_time:
            A[j] = last_reset_value

        A[j] += x
        last_query[j] = i
    else:  # query == 3
        j = args[0] - 1
        if last_query[j] < last_reset_time:
            A[j] = last_reset_value

        print(A[j])
        last_query[j] = i
