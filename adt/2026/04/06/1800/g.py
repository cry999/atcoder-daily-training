N = int(input())
SIZE = 2000
sky = [[0] * (SIZE + 2) for _ in range(SIZE + 2)]
clouds = []

for _ in range(N):
    u, d, l, r = map(int, input().split())
    sky[u][l] += 1
    sky[u][r + 1] -= 1
    sky[d + 1][l] -= 1
    sky[d + 1][r + 1] += 1

    clouds.append((u, d, l, r))

# まずは、雲がいくつ重なっているかを求めるための累積和を取る

# 横方向
for i in range(SIZE + 1):
    for j in range(SIZE):
        sky[i][j + 1] += sky[i][j]

# 縦方向
for i in range(SIZE):
    for j in range(SIZE + 1):
        sky[i + 1][j] += sky[i][j]

total = SIZE * SIZE
for i in range(SIZE + 1):
    for j in range(SIZE + 1):
        total -= sky[i][j] > 0
        # 値が 1 のところは雲が 1 つしかないので、雲を取り除く効果がある。
        # それ以外は関係ないので 0 にする。
        if sky[i][j] != 1:
            sky[i][j] = 0

# 雲を取り除く影響を計算できるように再度累積和を取る。

# 横方向
for i in range(SIZE + 1):
    for j in range(SIZE):
        sky[i][j + 1] += sky[i][j]

# 縦方向
for i in range(SIZE):
    for j in range(SIZE + 1):
        sky[i + 1][j] += sky[i][j]

for u, d, l, r in clouds:
    diff = sky[d][r] - sky[d][l - 1] - sky[u - 1][r] + sky[u - 1][l - 1]
    print(total + diff)
