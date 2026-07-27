from bisect import bisect_left

N = int(input())
(*A,) = map(int, input().split())

inc_line = [[] for _ in range(2)]

for a in A:
    i = bisect_left(inc_line[0], a)

    # 末尾に追加できるなら追加する。
    if i == len(inc_line[0]):
        inc_line[0].append(a)
        continue

    # 無理なら入れ替え。
    # 入れ替えることで順番がおかしくなるように見えるが、
    # 元々の入れ替える前の数字があったと仮定すればいいので問題ないはず。
    inc_line[0][i], a = a, inc_line[0][i]

    j = bisect_left(inc_line[1], a)

    if j == len(inc_line[1]):
        # 末尾に追加できるなら追加する。
        inc_line[1].append(a)
    else:
        # 無理ならいれかえ
        inc_line[1][j] = a

print(sum(len(l) for l in inc_line))
