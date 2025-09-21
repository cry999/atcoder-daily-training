T = int(input())


def efficient(S: list[list[str]], h: int, w: int) -> int:
    count = 0
    H, W = len(S), len(S[0])
    if h > 0 and w > 0:
        count += S[h-1][w] == S[h-1][w-1] == S[h][w-1] == S[h][w] == '#'
    if h > 0 and w < W-1:
        count += S[h-1][w] == S[h-1][w+1] == S[h][w+1] == S[h][w] == '#'
    if w > 0 and h < H-1:
        count += S[h+1][w] == S[h+1][w-1] == S[h][w-1] == S[h][w] == '#'
    if w < W-1 and h < H-1:
        count += S[h+1][w] == S[h+1][w+1] == S[h][w+1] == S[h][w] == '#'
    return count


def min_operation(S: list[list[str]]) -> int:
    count = 0
    H, W = len(S), len(S[0])
    for h in range(H-1):
        for w in range(W-1):
            if not (S[h][w] == S[h+1][w] == S[h][w+1] == S[h+1][w+1] == '#'):
                continue
            # 左上を白(.)に変えた場合の影響
            lu = efficient(S, h, w)
            # 右上を白(.)に変えた場合の影響
            ru = efficient(S, h, w+1)
            # 左下を白(.)に変えた場合の影響
            ld = efficient(S, h+1, w)
            # 右下を白(.)に変えた場合の影響
            rd = efficient(S, h+1, w+1)

            max_eff = max(lu, ru, ld, rd)
            # 同じ効率の場合、より多くの選択肢を試す
            if rd == max_eff:
                S[h+1][w+1] = '.'
            elif ld == max_eff:
                S[h+1][w] = '.'
            elif ru == max_eff:
                S[h][w+1] = '.'
            else:
                S[h][w] = '.'

            count += 1

    return count


for _ in range(T):
    H, W = map(int, input().split())
    S = [list(input()) for _ in range(H)]

    # S を 90 度回転させたものを考える
    S90 = [[''] * H for _ in range(W)]
    for h in range(H):
        for w in range(W):
            S90[w][H-1-h] = S[h][w]
    # S を 180 度回転させたものを考える
    S180 = [[''] * W for _ in range(H)]
    for h in range(H):
        for w in range(W):
            S180[H-1-h][W-1-w] = S[h][w]
    # S を 270 度回転させたものを考える
    S270 = [[''] * H for _ in range(W)]
    for h in range(H):
        for w in range(W):
            S270[W-1-w][h] = S[h][w]
    # S を反転する
    rev_S = [row[::-1] for row in S]
    # rev_s を 90 度回転させたものを考える
    rev_S90 = [[''] * H for _ in range(W)]
    for h in range(H):
        for w in range(W):
            rev_S90[w][H-1-h] = rev_S[h][w]
    # rev_s を 180 度回転させたものを考える
    rev_S180 = [[''] * W for _ in range(H)]
    for h in range(H):
        for w in range(W):
            rev_S180[H-1-h][W-1-w] = rev_S[h][w]
    # rev_s を 270 度回転させたものを考える
    rev_S270 = [[''] * H for _ in range(W)]
    for h in range(H):
        for w in range(W):
            rev_S270[W-1-w][h] = rev_S[h][w]

    count = min(
        min_operation(S),
        min_operation(S90),
        min_operation(S180),
        min_operation(S270),
        min_operation(rev_S),
        min_operation(rev_S90),
        min_operation(rev_S180),
        min_operation(rev_S270),
    )
    print(count)
