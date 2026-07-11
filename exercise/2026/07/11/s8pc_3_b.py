H, W, K = map(int, input().split())

original = [list(map(int, input())) for _ in range(H)]

ans = 0
for p0 in range(H * W):
    h0, w0 = divmod(p0, W)
    if h0 == 0:
        # 一番上の行を消しても変化ないので無駄
        continue

    # h0, w0 を最初にけして、スコアが幾つになるかを確かめる。
    # O((H*W)^3) 位かかりそうだが間に合うか?

    # 縦横入れ替えた方がやりやすいので入れ替える
    board = [[] for _ in range(W)]
    for p in range(H * W):
        h, w = divmod(p, W)
        if h == h0 and w == w0:
            continue
        board[w].append(original[h][w])
    for w in range(W):
        board[w].reverse()

    coeff = 1
    total_score = 0
    while True:
        this_time_score = 0
        for h in range(H):
            w = 0
            while w < W:
                if len(board[w]) <= h:
                    # この列は h 行も残ってないのでスキップ
                    w += 1
                    continue
                if board[w][h] == 0:
                    # すでに消えているのでスキップ
                    w += 1
                    continue
                d = 0
                c = board[w][h]
                while w + d < W and h < len(board[w + d]) and board[w + d][h] == c:
                    d += 1
                if d >= K:
                    d = 0
                    while w + d < W and h < len(board[w + d]) and board[w + d][h] == c:
                        this_time_score += c
                        board[w + d][h] = 0
                        d += 1
                w += d

        if this_time_score == 0:
            break
        total_score += this_time_score * coeff
        coeff *= 2
        for w in range(W):
            board[w] = [c for c in board[w] if c != 0]
    # print(f"[DEBUG] {h0=}, {w0=}, {total_score=}")
    # print(f"[DEBUG] === board ===")
    # for r in board:
    #     print(f"[DEBUG]   {r}")
    ans = max(ans, total_score)
print(ans)
