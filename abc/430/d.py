from sortedcontainers import SortedList


INF = 10**18

N = int(input())
X = list(map(int, input().split()))

total_dist = 0
pos = SortedList([0])


def dist(i: int) -> int:
    '''i 番目の位置の人から最も近い人までの距離を計算する'''
    if i < 0 or i >= len(pos):
        return INF
    return min(
        (pos[i]-pos[i-1]) if i > 0 else INF,
        (pos[i+1]-pos[i]) if i < len(pos)-1 else INF,
    )


for x in X:
    i = pos.bisect_left(x)

    # 挿入する一の前後の距離を total_dist から引いておく

    left_dist = dist(i-1)
    if left_dist != INF:
        total_dist -= left_dist

    right_dist = dist(i)
    if right_dist != INF:
        total_dist -= right_dist

    # 新しい人を挿入して、その人からの距離を total_dist に足す
    pos.add(x)

    left_dist = dist(i-1)
    if left_dist != INF:
        total_dist += left_dist

    new_dist = dist(i)
    total_dist += new_dist

    right_dist = dist(i+1)
    if right_dist != INF:
        total_dist += right_dist

    print(total_dist)
