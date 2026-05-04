M = 2000
sky = [[0] * (M + 2) for _ in range(M + 2)]
clouds = []

N = int(input())
for _ in range(N):
    u, d, l, r = map(int, input().split())
    clouds.append((u, d, l, r))

    sky[u][l] += 1
    sky[u][r + 1] -= 1
    sky[d + 1][l] -= 1
    sky[d + 1][r + 1] += 1

# まずは各箇所に雲がいくつあるかを計算する累積和
for i in range(M + 2):
    for j in range(M + 1):
        sky[i][j + 1] += sky[i][j]

for i in range(M + 1):
    for j in range(M + 2):
        sky[i + 1][j] += sky[i][j]

# 除外可能な雲の個数を累積和で計算したいので、複数の雲が重複している部分は除外する。
# 同時に、雲に覆われている箇所も計算しておく。
covered = 0
for i in range(M + 2):
    for j in range(M + 2):
        if sky[i][j]:
            covered += 1
        if sky[i][j] > 1:
            sky[i][j] = 0

# 累積和で雲の面積が取れるようにさらに累積和をとる。
for i in range(M + 2):
    for j in range(M + 1):
        sky[i][j + 1] += sky[i][j]

for i in range(M + 1):
    for j in range(M + 2):
        sky[i + 1][j] += sky[i][j]


for u, d, l, r in clouds:
    # 雲を除外していない状態の雲に覆われていない箇所
    ans = M * M - covered
    # 雲 k を除外して得られる追加の空を計算する。
    n = 0
    n += sky[d][r]
    n -= sky[d][l - 1]
    n -= sky[u - 1][r]
    n += sky[u - 1][l - 1]

    print(ans + n)
