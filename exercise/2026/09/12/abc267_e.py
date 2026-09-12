# >>> atcoder-stat >>>
# started_at  = 2026-09-12T17:10:25+09:00
# solved_at   = 2026-09-12T17:20:32+09:00
# duration_ms = 607265
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


N, M = map(int, input().split())
(*A,) = map(int, input().split())

g = [[] for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u, v = u - 1, v - 1
    g[u].append(v)
    g[v].append(u)

# 1. X 以下のコストで全ての操作を可能か
# 2. 全ての操作のコストは、各操作のコストの最大値なので、全ての操作が X 以下のコストかを考える
# 3. X 以下でできるようになった操作はいつ行っても良い。
# 4. したがって、X 以下のコストで削除可能になった頂点を随時削除していって、全て削除できれば良い。
# 5. O(N + M) で判定可能かな。

initial_scores = [sum(A[v] for v in g[u]) for u in range(N)]
scores = initial_scores[:]

lo, hi = -1, max(initial_scores)
while hi - lo > 1:
    x = (hi + lo) // 2
    print(f"[DEBUG] {lo=} ~ {hi=} : {x=}")

    for u in range(N):
        scores[u] = initial_scores[u]

    queue = [u for u in range(N) if scores[u] <= x]
    visited = [scores[u] <= x for u in range(N)]
    print(f"[DEBUG]   {queue=}")
    print(f"[DEBUG]   {visited=}")

    for u in queue:
        for v in g[u]:
            if visited[v]:
                continue
            scores[v] -= A[u]
            if scores[v] <= x:
                visited[v] = True
                queue.append(v)

    if all(visited):
        print(f"[DEBUG] -> OK")
        hi = x
    else:
        print(f"[DEBUG] -> NG")
        lo = x

print(hi)
