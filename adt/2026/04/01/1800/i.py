from collections import deque, Counter

N, K = map(int, input().split())
points = [tuple(map(int, input().split())) for _ in range(N)]

xs = deque(sorted(map(lambda x: [x[0], x[1]], Counter(x for x, _ in points).items())))
ys = deque(sorted(map(lambda y: [y[0], y[1]], Counter(y for _, y in points).items())))


def diff(s: deque[list[int]]):
    return s[-1][0] - s[0][0]


def update_head(s: deque[list[int]], d: int):
    s[0][0] += d
    if s[0][0] == s[1][0]:
        _, cnt = s.popleft()
        s[0][1] += cnt


def update_tail(s: deque[list[int]], d: int):
    s[-1][0] -= d
    if s[-1][0] == s[-2][0]:
        _, cnt = s.pop()
        s[-1][1] += cnt


while K and diff(xs) != diff(ys):
    if diff(xs) > diff(ys):
        xs, ys = ys, xs

    min_x, max_x = xs[0][0], xs[-1][0]
    min_y, max_y = ys[0][0], ys[-1][0]

    # 点の数が少ない方を以下を満たすまで移動する。
    # 1. K がなくなる
    # 2. max_y - min_y が max_x - min_x と同じになる
    # 3. min_y あるいは max_y が隣接する点と同じ位置になる
    _, min_y_cnt = ys[0]
    _, max_y_cnt = ys[-1]
    if min_y_cnt <= max_y_cnt:
        nxt_y, nxt_y_cnt = ys[1]
        move = min(
            K,
            min_y_cnt * (diff(ys) - diff(xs)),
            min_y_cnt * (nxt_y - min_y),
        )
        K -= move
        d = move // min_y_cnt
        update_head(ys, d)
    else:
        nxt_y, nxt_y_cnt = ys[-2]
        move = min(
            K,
            max_y_cnt * (diff(ys) - diff(xs)),
            max_y_cnt * (max_y - nxt_y),
        )
        K -= move
        d = move // max_y_cnt
        update_tail(ys, d)

while K and diff(xs) == diff(ys) and len(xs) > 1:
    # x, y を同じだけ動かす。それぞれ、点の数が少ない max or min を動かす。
    # 以下のいずれかの条件を満たすまで動かす.
    # 1. K がなくなる
    # 2. 隣接する点と同じ位置になる

    # x の選択
    if xs[0][1] < xs[-1][1]:
        dx = xs[1][0] - xs[0][0]
        xc = xs[0][1]
    else:
        dx = xs[-1][0] - xs[-2][0]
        xc = xs[-1][1]

    # y の選択
    if ys[0][1] < ys[-1][1]:
        dy = ys[1][0] - ys[0][0]
        yc = ys[0][1]
    else:
        dy = ys[-1][0] - ys[-2][0]
        yc = ys[-1][1]

    move = min(
        K,
        (xc + yc) * (min(dx, dy)),
    )
    K -= move
    d = move // (xc + yc)
    if xs[0][1] < xs[-1][1]:
        update_head(xs, d)
    else:
        update_tail(xs, d)

    if ys[0][1] < ys[-1][1]:
        update_head(ys, d)
    else:
        update_tail(ys, d)

if len(ys) == 1:
    # swap
    xs, ys = ys, xs

while K and len(xs) == 1 and len(ys) > 1:
    min_y, max_y = ys[0][0], ys[-1][0]

    # len(ys) == 1 の場合は while 条件で弾かれている。
    _, min_y_cnt = ys[0]
    _, max_y_cnt = ys[-1]
    if min_y_cnt <= max_y_cnt:
        nxt_y, nxt_y_cnt = ys[1]  # next
        move = min(K, min_y_cnt * (nxt_y - min_y))
        K -= move
        d = move // min_y_cnt
        update_head(ys, d)

    else:
        nxt_y, nxt_y_cnt = ys[-2]  # next
        move = max(K, max_y_cnt * (max_y - nxt_y))
        K -= move
        d = move // max_y_cnt
        update_tail(ys, d)

print(max(diff(xs), diff(ys)))
