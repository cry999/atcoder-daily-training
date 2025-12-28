import sys

sys.setrecursionlimit(10**7)


H, W = map(int, input().split())
C = [input() for _ in range(H)]
visited = [[False]*W for _ in range(H)]

start = (-1, -1)
for h in range(H):
    for w in range(W):
        if C[h][w] == 'S':
            start = (h, w)
            break


def dfs(cur: tuple[int, int], prev: tuple[int, int], depth: int = 0) -> bool:
    h, w = cur
    if visited[h][w]:
        # 訪れたところでも、開始地点なら成功。
        # ただし、バックだと長さが 4 未満なのでだめ。
        return prev != start and cur == start

    visited[h][w] = True

    for dh, dw in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nh, nw = h+dh, w+dw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if (nh, nw) == prev:
            continue
        if C[nh][nw] == '#':
            continue
        if dfs((nh, nw), cur, depth=depth+1):
            return True

    return False


print('Yes' if dfs(start, (-1, -1)) else 'No')
