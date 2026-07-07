import sys

input = sys.stdin.readline

H, W, N = map(int, input().split())
S = [input().rstrip() for _ in range(H)]

sh, sw = -1, -1
for h in range(H):
    for w in range(W):
        if S[h][w] == "S":
            sh, sw = h, w

hps = [-1] * (H * W)
steps = [-1] * (H * W)


# (h, w,  hitpoint)
s = sh * W + sw
q = [s]
hps[s], steps[s] = 1, 0
ADJ = [(1, 0), (-1, 0), (0, 1), (0, -1)]
for pos in q:
    h, w = divmod(pos, W)
    hp, step = hps[pos], steps[pos]
    for dh, dw in ADJ:
        nh, nw = h + dh, w + dw
        npos = nh * W + nw
        if not (0 <= nh < H and 0 <= nw < W):
            continue
        if S[nh][nw] == "X":
            continue

        next_hp, next_step = hps[npos], steps[npos]
        if hp == next_hp and next_step != -1:
            continue
        if hp < next_hp:
            continue

        n = -1
        if "1" <= S[nh][nw] <= "9":
            n = int(S[nh][nw])

        q.append(npos)
        if n != hp:
            hps[npos], steps[npos] = hp, step + 1
        else:
            hps[npos], steps[npos] = hp + 1, step + 1

        if n == hp == N:
            print(step + 1)
            exit()
