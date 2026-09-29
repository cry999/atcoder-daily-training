import bisect

N, Q = map(int, input().split())

# 考察:
# 1. 各ますのタイルが置かれていない期間を保持する。
# 2. 色を塗るクエリを順番に持っておく。
# 3. 1 の期間で 2 を含むものを探す。

is_tiled = [False] * N
last_empty = [0] * N
colors = [(0, "a")]

events = []
for i in range(Q):
    query, *args = input().split()
    if query == "1":
        x = int(args[0]) - 1
        # x のタイルをトグルする
        is_tiled[x] = not is_tiled[x]
        if is_tiled[x]:
            # last_empty[x] ~ i までタイルが乗ってなかった
            events.append((last_empty[x], i, x))
        else:
            last_empty[x] = i
    else:
        colors.append((i, args[0]))

for x in range(N):
    if not is_tiled[x]:
        events.append((last_empty[x], Q, x))

ans = ["a"] * N
for start, end, x in events:
    i = bisect.bisect_right(colors, (end, "")) - 1
    if i < len(colors) and start <= colors[i][0] <= end:
        ans[x] = colors[i][1]


print("".join(ans))
