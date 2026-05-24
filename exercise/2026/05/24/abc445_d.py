H, W, N = map(int, input().split())

# 1. H, W と一致する縦 or 横をもつピースを配置する。
# 2. 縦が一致している場合は W を減らし、横が一致している場合は H を減らす。
# 3. ピースが残っている限り 1 に戻る。

pieces = []
for i in range(N):
    h, w = map(int, input().split())
    pieces.append((h, w, i))

sort_by_h = sorted(pieces, key=lambda x: x[0])
sort_by_w = sorted(pieces, key=lambda x: x[1])
used = [False] * N

remain_h, remain_w = H, W
ans = [None] * N
pos_h, pos_w = 1, 1  # 次にピースを置く左上の座標
for _ in range(N):
    # まずはゴミ掃除しておく。
    while sort_by_h and used[sort_by_h[-1][-1]]:
        sort_by_h.pop()
    while sort_by_w and used[sort_by_w[-1][-1]]:
        sort_by_w.pop()

    if sort_by_h and sort_by_h[-1][0] == remain_h:
        _, w, i = sort_by_h.pop()
        used[i] = True
        remain_w -= w
        ans[i] = (pos_h, pos_w)
        pos_w += w
    else:
        h, _, i = sort_by_w.pop()
        used[i] = True
        remain_h -= h
        ans[i] = (pos_h, pos_w)
        pos_h += h

for h, w in ans:
    print(h, w)
