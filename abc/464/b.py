H, W = map(int, input().split())
S = [input() for _ in range(H)]

sh, sw, th, tw = 0, 0, H - 1, W - 1

for h in range(H):
    sh = h
    if S[h].count("#") != 0:
        break

for h in range(H - 1, sh - 1, -1):
    th = h
    if S[h].count("#") != 0:
        break

for w in range(W):
    sw = w
    for h in range(sh, th + 1):
        if S[h][w] == "#":
            break
    else:
        continue
    break

for w in range(W - 1, sw - 1, -1):
    tw = w
    for h in range(sh, th + 1):
        if S[h][w] == "#":
            break
    else:
        continue
    break

for h in range(sh, th + 1):
    for w in range(sw, tw + 1):
        print(S[h][w], end="")
    print()
