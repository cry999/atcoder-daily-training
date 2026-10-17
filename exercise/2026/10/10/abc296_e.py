# >>> atcoder-stat >>>
# started_at  = 2026-10-10T10:07:18+09:00
# solved_at   = 2026-10-10T10:30:12+09:00
# duration_ms = 1374499
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

sys.setrecursionlimit(10**6)


N = int(input())
(*A,) = map(int, input().split())

# 考察
# 1. 閉路に含まれる頂点は、任意の移動回数で到達可能
# 2. 閉路に含まれない頂点は、最長移動距離 + 1 を設定すれば到達不可能
# 3. 以上より、閉路に含まれるかいなか、と、閉路に含まれない頂点の最遠頂点との距離を記録すれば良い。


in_cycle = [False] * N
seen = [False] * N
finished = [False] * N

for i in range(N):
    if seen[i] or finished[i]:
        continue

    history = []

    u = i
    while not seen[u] and not finished[u]:
        seen[u] = True
        history.append(u)
        u = A[u] - 1

    if seen[u]:
        v = u
        while True:
            in_cycle[v] = True
            v = A[v] - 1
            if v == u:
                break

    for v in history:
        finished[v] = True

print(sum(in_cycle))
