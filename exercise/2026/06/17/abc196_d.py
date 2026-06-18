H, W, A, B = map(int, input().split())

state = [[0] * W for _ in range(H)]


def dfs(a: int, b: int, h: int, w: int):
    if a == 0:
        return 1

    nh, nw = divmod(h * W + w + 1, W)

    res = 0
    if state[h][w] == 1:
        res += dfs(a, b, nh, nw)
    else:
        state[h][w] = 1
        if a > 0:
            if w + 1 < W and state[h][w + 1] == 0:
                state[h][w + 1] = 1
                res += dfs(a - 1, b, nh, nw)
                state[h][w + 1] = 0
            if h + 1 < H and state[h + 1][w] == 0:
                state[h + 1][w] = 1
                res += dfs(a - 1, b, nh, nw)
                state[h + 1][w] = 0
        if b > 0:
            res += dfs(a, b - 1, nh, nw)
        state[h][w] = 0

    return res


print(dfs(A, B, 0, 0))
