import sys

sys.setrecursionlimit(10**7)

H, W = map(int, input().split())
A = [list(map(int, input().split())) for _ in range(H)]
used = [[False] * W for _ in range(H)]


def dfs(i: int):
    h = i // W
    w = i % W
    if h == H - 1 and w == W - 1:
        ans = 0
        for h in range(H):
            for w in range(W):
                if used[h][w]:
                    continue
                ans ^= A[h][w]
        return ans

    if used[h][w]:
        return dfs(i + 1)

    ans = dfs(i + 1)
    if h + 1 < H and not used[h + 1][w]:
        used[h][w] = used[h + 1][w] = True
        ans = max(ans, dfs(i + 1))
        used[h][w] = used[h + 1][w] = False
    if w + 1 < W and not used[h][w + 1]:
        used[h][w] = used[h][w + 1] = True
        ans = max(ans, dfs(i + 1))
        used[h][w] = used[h][w + 1] = False

    return ans


print(dfs(0))
