import sys

sys.setrecursionlimit(10**7)


N = int(input())
MOD = 10**9 + 7

graph = [[] for _ in range(N)]

for _ in range(N - 1):
    x, y = map(int, input().split())
    x, y = x - 1, y - 1

    graph[x].append(y)
    graph[y].append(x)


def dfs(u: int, parent: int) -> tuple[int, int]:
    """u が黒の時の場合の数と白の時の場合の数を返す。"""
    b, w = 1, 1
    for v in graph[u]:
        if v == parent:
            continue
        cb, cw = dfs(v, u)
        b *= cw
        b %= MOD
        w *= cb + cw
        w %= MOD
    return b, w


b, w = dfs(0, -1)
print((b + w) % MOD)
