H, W = map(int, input().split())

S = [input() for _ in range(H)]
T = [input() for _ in range(H)]

RS = sorted(hash(''.join(S[h][w] for h in range(H))) for w in range(W))
RT = sorted(hash(''.join(T[h][w] for h in range(H))) for w in range(W))

for i in range(W):
    if RS[i] != RT[i]:
        print('No')
        break
else:
    print('Yes')
