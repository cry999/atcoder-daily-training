import sys

input = sys.stdin.readline

N = int(input())

ranges = []
for _ in range(N):
    a, b = map(int, input().split())
    ranges.append((a, 1))
    ranges.append((a + b, -1))
ranges.sort(reverse=True)

c = 0
ans = [0] * (N + 1)
while ranges:
    l, d = ranges.pop()
    c += d
    while ranges and ranges[-1][0] == l:
        _, d = ranges.pop()
        c += d

    if ranges:
        ans[c] += ranges[-1][0] - l
print(*ans[1:])
