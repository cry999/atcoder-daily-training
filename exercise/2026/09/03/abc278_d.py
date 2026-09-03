# >>> atcoder-stat >>>
# started_at  = 2026-09-03T13:54:30+09:00
# solved_at   = 2026-09-03T14:02:54+09:00
# duration_ms = 504930
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from collections import deque
import sys

input = sys.stdin.readline


N = int(input())
(*A,) = map(int, input().split())

Q = int(input())
# applied_query1[i] := A[i] に適用された最新の query 1 のクエリ番号
applied_query1 = [-1] * N
last_query1_value = -1
last_query1_index = -1
# query2: A[i] に対する加算クエリ
query2 = [deque() for _ in range(N)]
for q in range(Q):
    query, *args = map(int, input().split())
    if query == 1:
        last_query1_index = q
        last_query1_value = args[0]
    elif query == 2:
        i, x = args
        i -= 1
        query2[i].append((q, x))

    else:  # query == 3
        i = args[0] - 1

        if applied_query1[i] < last_query1_index:
            applied_query1[i] = last_query1_index
            A[i] = last_query1_value

        while query2[i]:
            qq, xx = query2[i].popleft()
            if qq < applied_query1[i]:
                continue
            A[i] += xx

        print(A[i])
