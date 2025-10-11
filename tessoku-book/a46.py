import random
import math

N = int(input())
XY = [tuple(map(int, input().split())) for _ in range(N)]

# # ただ print するだけ
# # 600 / 1000 点でた
# for i in range(N):
#     print(i+1)
# print(1)

# # 最も近い都市に移動する貪欲法
# visited = [False] * N
# now = 0
# visited[now] = True
#
# print(now+1)
# for _ in range(N-1):
#     min_i, min_d = now, float('inf')
#     now_x, now_y = XY[now]
#     for i in range(N):
#         if visited[i]:
#             continue
#         if i == now:
#             continue
#         next_x, next_y = XY[i]
#         d = (now_x - next_x) ** 2 + (now_y - next_y) ** 2
#         if min_d < d:
#             continue
#         min_i, min_d = i, d
#
#     visited[min_i] = True
#     print(min_i+1)
#
# print(1)

# 局所探索法
a = [i % N for i in range(N+1)]
M = 200000  # 試行回数
T = 30  # 温度


def score(a: list[int]) -> int:
    return sum(
        (XY[a[i]][0]-XY[a[i+1]][0]) ** 2
        + (XY[a[i]][1]-XY[a[i+1]][1]) ** 2
        for i in range(N)
    )


best_score = score(a)
for i in range(M):
    left = random.randint(2, N)
    right = random.randint(2, N)
    if left > right:
        left, right = right, left

    s = score(a[:left] + a[right-1:left-1:-1] + a[right:])
    p = math.exp(min(-(s - best_score) / (T * (M-i) / M), 0))
    if s < best_score:
        a = a[:left] + a[right-1:left-1:-1] + a[right:]
        best_score = s
    elif p > random.random():
        a = a[:left] + a[right-1:left-1:-1] + a[right:]
        best_score = s

for v in a:
    print(v+1)
