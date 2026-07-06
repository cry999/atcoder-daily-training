from itertools import permutations

k = int(input())
queen = [-1] * 8
for _ in range(k):
    r, c = map(int, input().split())
    queen[r] = c

for place in permutations(range(8)):
    ok = True
    for r in range(8):
        if queen[r] == -1:
            continue
        if queen[r] == place[r]:
            continue
        ok = False
        break

    if not ok:
        continue

    board = [[True] * 8 for _ in range(8)]
    ok = True
    for r in range(8):
        c = place[r]
        if not board[r][c]:
            ok = False
            break

        for d in range(1, 8):
            if r + d >= 8 or c + d >= 8:
                break
            board[r + d][c + d] = False
        for d in range(1, 8):
            if r + d >= 8 or c - d < 0:
                break
            board[r + d][c - d] = False

    if not ok:
        continue

    for r in range(8):
        print("".join("Q" if c == place[r] else "." for c in range(8)))
