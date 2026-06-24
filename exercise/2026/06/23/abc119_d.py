from bisect import bisect_left
import sys

input = sys.stdin.readline

INF = 10**18

A, B, Q = map(int, input().split())

s = [-INF] + [int(input()) for _ in range(A)] + [INF]
t = [-INF] + [int(input()) for _ in range(B)] + [INF]

for _ in range(Q):
    x = int(input())

    i = bisect_left(s, x)
    j = bisect_left(t, x)

    s_left, s_right = s[i - 1], s[i]
    t_left, t_right = t[j - 1], t[j]

    ans = min(
        max(s_right, t_right) - x,  # 東に走り続けるのが最短
        x - min(s_left, t_left),  # 西に走り続けるのが最短
        # 折り返すパターン
        2 * min(x - s_left, t_right - x) + max(x - s_left, t_right - x),
        2 * min(x - t_left, s_right - x) + max(x - t_left, s_right - x),
    )
    print(ans)
