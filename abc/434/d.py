MAX = 2000
N = int(input())

clouds = []

# 累積和
cum = [[0] * (MAX+2) for _ in range(MAX+2)]

# for debug print
MIN_U, MIN_L, MAX_D, MAX_R = MAX+1, MAX+1, 0, 0

for _ in range(N):
    U, D, L, R = map(int, input().split())
    cum[U][L] += 1
    cum[U][R+1] -= 1
    cum[D+1][L] -= 1
    cum[D+1][R+1] += 1
    MIN_U, MIN_L = min(MIN_U, U), min(MIN_L, L)
    MAX_D, MAX_R = max(MAX_D, D), max(MAX_R, R)
    clouds.append((U, D, L, R))

# 横方向
for i in range(MAX+2):
    for j in range(MAX+1):
        cum[i][j+1] += cum[i][j]
# 縦方向
for j in range(MAX+2):
    for i in range(MAX+1):
        cum[i+1][j] += cum[i][j]

# この時点で cum[i][j] > 0 以上の部分を数えて雲に覆われている部分を計算しておく。
total_clouds = sum(cum[i][j] > 0
                   for i in range(1, MAX+1)
                   for j in range(1, MAX+1))

# 2 以上のマスを 0 にする
for i in range(1, MAX+1):
    for j in range(1, MAX+1):
        if cum[i][j] > 1:
            cum[i][j] = 0

# 面積を求めたいのでさらに累積和をとる
# 横方向
for i in range(MAX+2):
    for j in range(MAX+1):
        cum[i][j+1] += cum[i][j]
# 縦方向
for j in range(MAX+2):
    for i in range(MAX+1):
        cum[i+1][j] += cum[i][j]

# これで、cum[D][R] - cum[U-1][R] - cum[D][L-1] + cum[U-1][L-1] が
# [U, D] x [L, R] の雲で覆われているマス目の数になる。
for U, D, L, R in clouds:
    area = cum[D][R] - cum[U-1][R] - cum[D][L-1] + cum[U-1][L-1]
    # print(U, D, L, R, area)
    print(2000**2 - total_clouds + area)

# debug print
# for i in range(MIN_U, MAX_D+1):
#     print(*cum[i][MIN_L:MAX_R+1])
