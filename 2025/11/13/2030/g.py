H, W = map(int, input().split())

A = [list(map(int, input().split())) for _ in range(H)]

possible_dominos = []
visit = [False]*(H*W)
visit[0] = True
queue = [0]

while queue:
    state_bit = queue.pop()


max_score = 0
# i = 0 は scroe = 0 確定なのでスキップ
for i in range(1, 1 << (H*W)):
    score = 0
    not_uses = []
    uses = []
    expected_walls = [[False] * W for _ in range(H)]
    for h in range(H):
        for w in range(W):
            if not i & (1 << (h*W + w)):
                not_uses.append((h, w))
                expected_walls[h][w] = True
                continue
            score |= A[h][w]
            # print(f'uses: ({h}, {w}): {score=}')
            uses.append((h, w))
    if score <= max_score:
        continue
    # 次に、この選択が可能かどうかを確認する。
    walls = [[False]*W for _ in range(H)]

print(max_score)
