import sys

input = sys.stdin.readline

N, X = map(int, input().split())

# dp[i] := i 円を払えるか
dp = [False] * (X + 1)
dp[0] = True

for _ in range(N):
    a, b = map(int, input().split())

    for x in range(X, -1, -1):
        for y in range(b + 1):
            if dp[x]:
                break
            if x - a * y < 0:
                break
            dp[x] = dp[x - a * y]

print("Yes" if dp[X] else "No")
