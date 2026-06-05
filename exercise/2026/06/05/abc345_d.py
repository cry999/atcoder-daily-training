from itertools import combinations, permutations

N, H, W = map(int, input().split())

tiles = [tuple(map(int, input().split())) for _ in range(N)]

FULL = (1 << (H * W)) - 1

for i in range(1, N + 1):
    for comb in combinations(tiles, i):
        for perm in permutations(comb):
            for bit in range(1 << i):
                s = sum(h * w for h, w in perm)
                if s != H * W:
                    continue

                board = 0
                for j, (th, tw) in enumerate(perm):
                    if bit & (1 << j):
                        if th == tw:
                            break
                        th, tw = tw, th
                    mask = (1 << tw) - 1
                    # print(tw, j, f"{mask:0{W}b}")
                    ok = False
                    for pos in range(H * W):
                        h, w = divmod(pos, W)
                        if board & (mask << (h * W + w)):
                            continue
                        if h + th > H:
                            continue
                        if w + tw > W:
                            break
                        for dh in range(th):
                            board |= mask << ((h + dh) * W + w)
                        ok = True
                        break
                if board == FULL:
                    print("Yes")
                    exit()

print("No")
