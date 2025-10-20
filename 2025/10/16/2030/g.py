# 全探索でいける
# O(N!2^N) で N=6 なので、46080 回くらい。十分間に合う

from itertools import permutations
from math import sqrt

N, S, T = map(int, input().split())
lines = [tuple(map(int, input().split())) for _ in range(N)]

min_time = float('inf')
for permutated_lines in permutations(lines):
    for bit in range(1 << N):
        time, cursor = 0, (0, 0)
        for i, (xa, ya, xb, yb) in enumerate(permutated_lines):
            if (bit >> i) & 1:
                # bit が立っていたら端点を入れ替える
                xa, ya, xb, yb = xb, yb, xa, ya
            x, y = cursor
            # まずは、cursor から (xa, ya) へ速度 S で移動
            time += sqrt((x-xa)**2 + (y-ya)**2) / S
            # 次に、(xa, ya) -> (xb, yb) を速度 T で移動
            time += sqrt((xa-xb)**2 + (ya-yb)**2) / T
            # 最後に cursor を (xb, yb) に更新
            cursor = (xb, yb)

        min_time = min(min_time, time)

print(min_time)
