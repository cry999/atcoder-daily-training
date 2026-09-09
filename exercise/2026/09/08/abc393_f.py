# >>> atcoder-stat >>>
# started_at  = 2026-09-08T15:58:45+09:00
# solved_at   = 2026-09-08T16:15:21+09:00
# duration_ms = 996881
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from bisect import bisect_left
import sys

input = sys.stdin.readline


N, Q = map(int, input().split())
(*A,) = map(int, input().split())

# クエリを先読みする。
# R の小さい順に答えを求める。
# LIS を求める。
# A[R[i]] まで LIS を求めた時の、末尾が X[i] 以下の最大の部分列を求める。
# LIS をやっているから、長さに対する最小の末尾は持っている。
# それを X[i] で二分探索すれば答えは出る。

# (R, X)
queries = []
for i in range(Q):
    r, x = map(int, input().split())
    queries.append((r, x, i))
queries.sort()

INF = 10**18
L = [INF] * (N + 3)
L[0] = -INF
k = 0
ans = [0] * Q
for r, x, q in queries:
    while k < r:
        j = bisect_left(L, A[k])
        L[j] = A[k]
        k += 1

    j = bisect_left(L, x)
    if L[j] == x:
        j += 1
    print(f"[DEBUG] {r=}, {x=}, {L=}, {j=}")
    ans[q] = j - 1
for a in ans:
    print(a)
