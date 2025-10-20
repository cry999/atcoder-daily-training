N = int(input())
XY = [tuple(map(int, input().split())) for _ in range(N)]
S = input()
# g[y] = (
#   y 上で右に動く人の x 座標の最小値,
#   y 上で左に動く人の x 座標の最大値,
# )
g = {}

for i in range(N):
    direction = S[i]
    x, y = XY[i]

    if y not in g:
        if direction == 'R':
            g[y] = (x, -1)
        else:
            g[y] = (float('inf'), x)
    else:
        if direction == 'R':
            g[y] = (min(x, g[y][0]), g[y][1])
        else:
            g[y] = (g[y][0], max(x, g[y][1]))

for min_r, max_l in g.values():
    if min_r < max_l:
        print('Yes')
        break
else:
    print('No')
