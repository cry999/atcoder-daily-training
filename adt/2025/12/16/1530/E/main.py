H, W = map(int, input().split())
S = [input() for _ in range(H)]

a, b, c, d = float('inf'), 0, float('inf'), 0

for i in range(H):
    for j in range(W):
        if S[i][j] != '#':
            continue
        a, b = min(a, i), max(b, i)
        c, d = min(c, j), max(d, j)

for i in range(a, b+1):
    for j in range(c, d+1):
        if S[i][j] == '.':
            print(i+1, j+1)
