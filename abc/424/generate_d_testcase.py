MAX_H, MAX_W = 6, 6
MIN_H, MIN_W = 5, 5
count = sum(
    1 << (h+w)
    for h in range(MIN_H, MAX_H+1) for w in range(MIN_W, MAX_W+1)
)
print(count)
for H in range(MIN_H, MAX_H+1):
    for W in range(MIN_W, MAX_W+1):
        count = 0
        for i in range(1 << (H+W)):
            S = []
            for h in range(H):
                S.append(['.'] * W)
                for w in range(W):
                    if (i >> (h+w)) & 1:
                        S[h][w] = '#'
            print(H, W)
            print('\n'.join(''.join(row) for row in S))
