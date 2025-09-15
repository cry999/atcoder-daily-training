H, W = map(int, input().split())
S = [input() for _ in range(H)]

# H, W それぞれの方向で、黒が存在する位置の最大値・最小値を取得する。
# その中に白が存在すればアウト。

b_h_min, b_h_max = H, 0
b_w_min, b_w_max = W, 0

for h in range(H):
    for w in range(W):
        if S[h][w] == '#':
            b_h_min = min(b_h_min, h)
            b_h_max = max(b_h_max, h)
            b_w_min = min(b_w_min, w)
            b_w_max = max(b_w_max, w)


for h in range(b_h_min, b_h_max + 1):
    for w in range(b_w_min, b_w_max + 1):
        if S[h][w] == '.':
            print('No')
            break
    else:
        continue
    break
else:
    print('Yes')
