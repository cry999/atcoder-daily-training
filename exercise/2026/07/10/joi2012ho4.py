N, M = map(int, input().split())

cum = [[0] * (N + 3) for _ in range(N + 3)]

for _ in range(M):
    a, b, x = map(int, input().split())
    cum[a][b] += 1
    cum[a][b + 1] -= 1
    cum[a + x + 1][b] -= 1
    cum[a + x + 1][b + x + 2] += 1
    cum[a + x + 2][b + 1] += 1
    cum[a + x + 2][b + x + 2] -= 1

# 横
for a in range(N + 3):
    for b in range(N + 2):
        cum[a][b + 1] += cum[a][b]
# 縦
for a in range(N + 2):
    for b in range(N + 3):
        cum[a + 1][b] += cum[a][b]

# 斜め
for a in range(N + 2):
    for b in range(N + 2):
        cum[a + 1][b + 1] += cum[a][b]

print(sum(sum(map(lambda x: x > 0, r)) for r in cum))
