# >>> atcoder-stat >>>
# started_at  = 2026-08-26T17:01:24+09:00
# solved_at   = 2026-08-26T17:33:37+09:00
# duration_ms = 1933684
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 3
# complexity  = 3
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline
sys.setrecursionlimit(10**6)


T = int(input())
for _ in range(T):
    N, M = map(int, input().split())
    g = [[] for _ in range(N)]
    for _ in range(M):
        a, b = map(int, input().split())
        a, b = a - 1, b - 1
        g[a].append(b)
        g[b].append(a)

    seen = [False] * N
    finished = [False] * N

    parent = [-1] * N
    depth = [0] * N

    cycle = []

    def dfs(u: int, p: int = -1):
        seen[u] = True

        for v in g[u]:
            if v == p:  # 逆戻り
                continue
            if not seen[v]:  # 未訪問なら訪問
                parent[v] = u
                depth[v] = depth[u] + 1

                if dfs(v, u):
                    return True
            elif not finished[u] and depth[u] % 2 == depth[v] % 2:
                # 奇数長の閉路を見つけた場合, 閉路を復元して True を返す
                cur = u
                while cur != v:
                    cycle.append(cur + 1)
                    cur = parent[cur]

                cycle.append(v + 1)
                return True

        finished[u] = True
        return False

    if dfs(0):
        print(len(cycle))
        print(*cycle)
    else:
        print(-1)
