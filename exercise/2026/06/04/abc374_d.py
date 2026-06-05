from math import sqrt
from itertools import permutations

N, S, T = map(int, input().split())
lines = [tuple(map(int, input().split())) for _ in range(N)]

ans = float("inf")
for perm in permutations(range(N)):
    for dir in range(1 << N):
        t = 0
        x, y = 0, 0
        for i in perm:
            a, b, c, d = lines[i]
            if dir >> i & 1:  # 向きを逆にする
                c, d, a, b = a, b, c, d
            # (x, y) -> (a, b): S でいどう
            d1 = sqrt((x - a) ** 2 + (y - b) ** 2)
            t1 = d1 / S
            # (a, b) -> (c, d): T で移動
            d2 = sqrt((a - c) ** 2 + (b - d) ** 2)
            t2 = d2 / T

            t += t1 + t2
            x, y = c, d
        ans = min(ans, t)
print(ans)
