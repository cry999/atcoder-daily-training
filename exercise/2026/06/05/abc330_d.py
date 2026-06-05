N = int(input())
S = [input() for _ in range(N)]

# それぞれ、行 i の o の個数、列 j の o の個数
rows = [0] * N
cols = [0] * N

ans = 0
for ri, rj in [
    (range(N), range(N)),  # 左上に直角
    (range(N), range(N - 1, -1, -1)),  # 右上に直角
    (range(N - 1, -1, -1), range(N)),  # 左下に直角
    (range(N - 1, -1, -1), range(N - 1, -1, -1)),  # 右下に直角
]:
    # 集計
    for i in range(N):
        for j in range(N):
            if S[i][j] != "o":
                continue
            rows[i] += 1
            cols[j] += 1

    for i in ri:
        for j in rj:
            if S[i][j] != "o":
                continue
            # まずは自分をのぞいておく
            rows[i] -= 1
            cols[j] -= 1

            ans += rows[i] * cols[j]

print(ans)
