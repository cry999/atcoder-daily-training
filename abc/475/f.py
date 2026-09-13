import sys

input = sys.stdin.readline

H, W = map(int, input().split())
if H > W:
    white = [[""] * H for _ in range(W)]
    for h in range(H):
        s = input().strip()
        for w in range(W):
            white[w][h] = s[w] == "."
    H, W = W, H
else:
    white = [[c == "." for c in input().strip()] for _ in range(H)]


# 黒マスがあれば、その1マスだけ塗ることで変更なしにできる
ans = 1

# white_exists[c]: top〜bottom の列 c に白マスがある
white_exists = [False] * W
for u in range(H):
    top_row = white[u]

    # 初期化
    for c in range(W):
        white_exists[c] = False

    for d in range(u, H):
        bottom_row = white[d]

        # prefix[k]: 白ますが存在する列の累積和
        prefix = [0] * (W + 1)
        count = 0

        last_top = -1
        last_bottom = -1

        for r in range(W):
            if bottom_row[r]:
                white_exists[r] = True
                last_bottom = r

            if top_row[r]:
                last_top = r

            if white_exists[r]:
                count += 1

            prefix[r + 1] = count

            if not white_exists[r]:
                continue

            limit = min(last_top, last_bottom)

            ans += prefix[limit + 1]

print(ans)
