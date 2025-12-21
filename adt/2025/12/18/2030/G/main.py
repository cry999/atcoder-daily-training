H, W = map(int, input().split())
C = [list(map(lambda x: ord(x)-ord('a'), input())) for _ in range(H)]
rcnt = [[0]*26 for _ in range(H)]
ccnt = [[0]*26 for _ in range(W)]

for h in range(H):
    for w in range(W):
        rcnt[h][C[h][w]] += 1
        ccnt[w][C[h][w]] += 1

rlen, clen = H, W
r_ignore = [False]*H
c_ignore = [False]*W

for _ in range(H+W):
    remove_row = []
    for h in range(H):
        if r_ignore[h]:
            continue
        for c in range(26):
            if rcnt[h][c] == clen and rcnt[h][c] >= 2:
                remove_row.append((h, c))

    remove_col = []
    for w in range(W):
        if c_ignore[w]:
            continue
        for c in range(26):
            if ccnt[w][c] == rlen and ccnt[w][c] >= 2:
                remove_col.append((w, c))

    for h, c in remove_row:
        r_ignore[h] = True
        for w in range(W):
            ccnt[w][c] -= 1
        rlen -= 1

    for w, c in remove_col:
        c_ignore[w] = True
        for h in range(H):
            rcnt[h][c] -= 1
        clen -= 1

print(rlen*clen)
