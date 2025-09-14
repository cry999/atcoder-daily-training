N = int(input())
A = list(map(int, input().split()))
B = list(map(int, input().split()))

dp = [(0, None)] * N

dp[0] = (0, None)
dp[1] = (A[0], 0)

for i in range(2, N):
    c1, _ = dp[i-2]
    c2, _ = dp[i-1]
    # print(c1, c2, A[i-1], B[i-2])
    if c1 + B[i-2] < c2 + A[i-1]:
        dp[i] = (c1 + B[i-2], i-2)
    else:
        dp[i] = (c2 + A[i-1], i-1)

# print(dp)
prev = N-1
steps = [N]
while True:
    _, prev = dp[prev]
    if prev is None:
        break
    steps.append(prev+1)

print(len(steps))
print(*steps[::-1])
