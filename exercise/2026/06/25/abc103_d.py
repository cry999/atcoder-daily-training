import sys

input = sys.stdin.readline


N, M = map(int, input().split())
conflicts = []
for _ in range(M):
    a, b = map(int, input().split())
    conflicts.append((a, b))
conflicts.sort()

min_r = N + 1
j = 0
ans = 0
for i in range(1, N + 1):
    print(f"[DEBUG] {i=} {min_r=}")
    if i == min_r:
        # ここでぶった斬る。
        ans += 1
        min_r = N + 1

    while j < M and conflicts[j][0] == i:
        _, b = conflicts[j]
        min_r = min(min_r, b)
        j += 1

print(ans)
