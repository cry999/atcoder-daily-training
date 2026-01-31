from sortedcontainers import SortedDict
from collections import deque

N, K = map(int, input().split())

# x, y それぞれの出現回数をカウントするだけ。
hist_x = SortedDict()
hist_y = SortedDict()

for _ in range(N):
    x, y = map(int, input().split())

    hist_x[x] = hist_x.get(x, 0) + 1
    hist_y[y] = hist_y.get(y, 0) + 1


x_items: deque[tuple[int, int]] = deque(hist_x.items())
y_items: deque[tuple[int, int]] = deque(hist_y.items())

# K は操作回数
while K:
    # 操作方針。
    # - まとめて動かす。
    # - x と y の幅の大きい方を優先する。(幅を最小化するのが目標)
    # - x と y の大きい方を小さい方と同じ幅になるまで動かす。
    # - x と y が同じ幅になったら、同時に縮めていく。
    # - x, y それぞれを動かす時、最大・最小どちらを動かすか問題があるが、
    #   同じ座標にある点が少ない方を優先する(コストを最小化したい)

    gap_x = x_items[-1][0] - x_items[0][0]
    gap_y = y_items[-1][0] - y_items[0][0]

    if not gap_x and not gap_y:
        # もう動かす必要がない
        break

    mov_x, num_x, sig_x = 0, 0, 0
    mov_y, num_y, sig_y = 0, 0, 0
    if gap_x:
        if x_items[-1][1] > x_items[0][1]:
            # 最小を動かす方が得
            mov_x = x_items[1][0] - x_items[0][0]  # 動かす距離
            num_x = x_items[0][1]  # 動かす点の個数
            sig_x = -1  # 最小を動かす
        else:
            # 最大を動かす方が得
            mov_x = x_items[-1][0] - x_items[-2][0]  # 動かす距離
            num_x = x_items[-1][1]  # 動かす点の個数
            sig_x = 1  # 最大を動かす
    if gap_y:
        if y_items[-1][1] > y_items[0][1]:
            # 最小を動かす方が得
            mov_y = y_items[1][0] - y_items[0][0]  # 動かす距離
            num_y = y_items[0][1]  # 動かす点の個数
            sig_y = -1  # 最小を動かす
        else:
            # 最大を動かす方が得
            mov_y = y_items[-1][0] - y_items[-2][0]  # 動かす距離
            num_y = y_items[-1][1]  # 動かす点の個数
            sig_y = 1  # 最大を動かす

    ope_x, ope_y = 0, 0
    if gap_x > gap_y:
        # x だけを動かす。
        ope_x = min(
            K // num_x,  # num_x 個の点を何回動かせるか？
            mov_x,  # 動かす距離の最大値 (隣の座標までの距離)
            gap_x - gap_y,  # y の幅より小さくはしたくない
        )
        if not ope_x:
            # 動かしても意味がない or 動かせない
            break

        K -= ope_x * num_x
    elif gap_x < gap_y:
        # y だけを動かす。
        ope_y = min(
            K // num_y,  # num_y 個の点を何回動かせるか？
            mov_y,  # 動かす距離の最大値 (隣の座標までの距離)
            gap_y - gap_x,  # x の幅より小さくはしたくない
        )
        if not ope_y:
            # 動かしても意味がない or 動かせない
            break

        K -= ope_y * num_y
    else:
        # 両方動かす。
        ope = min(
            K // (num_x + num_y),  # num_x + num_y 個の点を何回動かせるか？
            min(mov_x, mov_y),  # 動かす距離の最大値 (隣の座標までの距離)
        )

        if not ope:
            break

        K -= ope * (num_x + num_y)
        ope_x = ope_y = ope

    if ope_x:
        if sig_x > 0:
            x, num = x_items.pop()
            if x - ope_x == x_items[-1][0]:
                x_items[-1] = (x - ope_x, x_items[-1][1] + num)
            else:
                x_items.append((x - ope_x, num))
        else:
            x, num = x_items.popleft()
            if x + ope_x == x_items[0][0]:
                x_items[0] = (x + ope_x, x_items[0][1] + num)
            else:
                x_items.appendleft((x + ope_x, num))
    if ope_y:
        if sig_y > 0:
            y, num = y_items.pop()
            if y - ope_y == y_items[-1][0]:
                y_items[-1] = (y - ope_y, y_items[-1][1] + num)
            else:
                y_items.append((y - ope_y, num))
        else:
            y, num = y_items.popleft()
            if y + ope_y == y_items[0][0]:
                y_items[0] = (y + ope_y, y_items[0][1] + num)
            else:
                y_items.appendleft((y + ope_y, num))

gap_x = x_items[-1][0] - x_items[0][0]
gap_y = y_items[-1][0] - y_items[0][0]
print(max(gap_x, gap_y))
