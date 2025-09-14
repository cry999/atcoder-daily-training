N = int(input())
h = list(map(int, input().split()))

dp = [(0, None)] * N
dp[0] = (0, None)
dp[1] = (abs(h[1]-h[0]), 0)

for i in range(2, N):
    c1, c2 = dp[i-1][0] + abs(h[i] - h[i-1]), dp[i-2][0] + abs(h[i] - h[i-2])
    dp[i] = (c1, i-1) if c1 < c2 else (c2, i-2)

steps = [N]
while True:
    _, prev = dp[steps[-1]-1]
    if prev is None:
        break
    steps.append(prev+1)

print(len(steps))
print(*steps[::-1])
