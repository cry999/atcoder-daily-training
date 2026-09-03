# >>> atcoder-stat >>>
# started_at  = 2026-09-02T14:34:10+09:00
# solved_at   = 2026-09-02T14:58:49+09:00
# duration_ms = 1479493
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
from collections import deque

N = int(input())
(*A,) = map(int, input().split())

Q = int(input())

# 最後の query 1
last_query_1_index = -1
last_query_1_value = -1
# 各 A[i] に対する query 2 のリスト
queries_2 = [deque() for _ in range(N)]
# 各 A[i] に対する 最後に適用した query_1 のインデックス
last_query_1_applied = [-1] * N

for q in range(Q):
    query, *args = map(int, input().split())

    if query == 1:
        x = args[0]
        last_query_1_index = q
        last_query_1_value = x
    elif query == 2:
        i, x = args
        queries_2[i - 1].append((q, x))
    else:  # q == 3
        i = args[0] - 1

        if last_query_1_applied[i] < last_query_1_index:
            A[i] = last_query_1_value
            last_query_1_applied[i] = last_query_1_index

        while queries_2[i]:
            prev_q, prev_x = queries_2[i].popleft()
            if prev_q < last_query_1_index:
                continue
            A[i] += prev_x

        print(A[i])
