# >>> atcoder-stat >>>
# started_at  = 2026-10-10T10:30:38+09:00
# solved_at   = 2026-10-10T10:55:45+09:00
# duration_ms = 1507478
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
# 1. ABC296 E と大体同じ？
# 2. サイクルに含まれる頂点は、全て互いに到達可能。 したがって、N * N 個のペア
# 3. サイクルに含まれない頂点は、dfs で求められる。u から始めて dfs(A[u]) で到達する全ての点が u のペアになる。

in_cycle = [False] * N
seen = [False] * N
finished = [False] * N


# dp[u] = u が到達する頂点の数
# dp[u in cycle] = size(cycle)
# dp[u not in cycle] = dp[A[u]] + 1
dp = [0] * N

for i in range(N):
    if seen[i] or finished[i]:
        continue

    history = []

    u = i
    while not seen[u] and not finished[u]:
        seen[u] = True
        history.append(u)
        u = A[u] - 1

    if not finished[u]:
        v = u
        size = 0
        while True:
            in_cycle[v] = True
            v = A[v] - 1
            if v == u:
                break
            size += 1

        v = u
        while True:
            dp[v] = size + 1
            v = A[v] - 1
            if v == u:
                break

    for v in history:
        finished[v] = True


def dfs(u: int):
    if in_cycle[u]:
        return dp[u]
    if dp[u] != 0:
        return dp[u]
    dp[u] = dfs(A[u] - 1) + 1
    return dp[u]


ans = sum(dfs(u) for u in range(N))
print(ans)
