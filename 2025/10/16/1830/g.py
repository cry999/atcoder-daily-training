H, W, K = map(int, input().split())
S = [input() for _ in range(H)]


visited = [[False] * W for _ in range(H)]


def dfs(h: int, w: int, depth: int) -> int:
    if h < 0 or H <= h or w < 0 or W <= w:
        return 0
    if visited[h][w] or S[h][w] == '#':
        return 0
    if depth == K:
        return 1
    visited[h][w] = True
    cnt = sum(
        dfs(h+dh, w+dw, depth+1)
        for dh, dw in [(1, 0), (-1, 0), (0, 1), (0, -1)]
    )
    visited[h][w] = False
    return cnt


# 深さ優先探索を全てのマスから開始する全探索
print(sum(
    dfs(sh, sw, 0)
    for (sh, sw) in [(h, w) for h in range(H) for w in range(W)]
))
