T = int(input())

for _ in range(T):
    N, M, X, Y = map(int, input().split())
    edges = [tuple(map(int, input().split())) for _ in range(M)]
    edges.sort()
    graph = [[] for _ in range(N + 1)]

    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    ans = []
    visited = [False] * (N + 1)

    def dfs(src: int, dst: int) -> bool:
        global ans

        if visited[src]:
            return False
        visited[src] = True

        if src == dst:
            ans.append(src)
            return True

        for nxt in graph[src]:
            if visited[nxt]:
                continue
            if dfs(nxt, dst):
                ans.append(src)
                return True

        return False

    if dfs(X, Y):
        print(*ans[::-1])
