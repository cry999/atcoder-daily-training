H, W = map(int, input().split())
C = [input() for _ in range(H)]

X = [sum(C[h][w] == "#" for h in range(H)) for w in range(W)]
print(*X)
