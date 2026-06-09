from sortedcontainers import SortedList

N = int(input())
(*X,) = map(int, input().split())

arrived = SortedList()
arrived.add(0)

total_neighbor_dist = 0

for x in X:
    i = arrived.bisect_left(x)
    if len(arrived) == 1:
        total_neighbor_dist += 2 * x
    elif i == len(arrived):
        # 一番大外
        # お隣さんの現在の最も近い距離を計算
        if i - 2 >= 0:
            old_dist = arrived[-1] - arrived[-2]
        else:
            old_dist = 0
        # 新規追加の x とお隣さんとの距離も計算
        new_dist = x - arrived[-1]
        # x の影響で new_dist は一回は追加される。
        total_neighbor_dist += new_dist
        # old_dist -> new_dist に変更されるのは new_dist の方が小さい時のみ
        if new_dist < old_dist:
            total_neighbor_dist += new_dist - old_dist
    else:
        # 条件により、確実に 0 < i < len(arrived)
        # 左隣の人から計算する。
        old_left_dist = arrived[i] - arrived[i - 1]
        if i - 2 >= 0:
            old_left_dist = min(old_left_dist, arrived[i - 1] - arrived[i - 2])

        # 右隣の人も計算する
        old_right_dist = arrived[i] - arrived[i - 1]
        if i + 1 < len(arrived):
            old_right_dist = min(old_right_dist, arrived[i + 1] - arrived[i])

        new_dist = min(arrived[i] - x, x - arrived[i - 1])
        total_neighbor_dist += new_dist

        if x - arrived[i - 1] < old_left_dist:
            total_neighbor_dist += (x - arrived[i - 1]) - old_left_dist
        if arrived[i] - x < old_right_dist:
            total_neighbor_dist += (arrived[i] - x) - old_right_dist

    arrived.add(x)
    print(total_neighbor_dist)
