import sys

input = sys.stdin.readline
N, X = map(int, input().split())

s = 0
ans = float("inf")
for i in range(N):
    a, b = map(int, input().split())
    if i < X:
        s += a + b
    ans = min(ans, s + max(X - i - 1, 0) * b)
print(ans)
