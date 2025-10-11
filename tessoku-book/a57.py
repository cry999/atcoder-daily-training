N, Q = map(int, input().split())
A = list(map(int, input().split()))

dp = [[0] * N for _ in range(32)]
for i in range(N):
    dp[0][i] = A[i]-1


for j in range(31):
    for i in range(N):
        dp[j+1][i] = dp[j][dp[j][i]]

# print(dp)
for _ in range(Q):
    X, Y = map(int, input().split())
    cur = X-1
    j = 0
    while Y:
        if Y & (1 << j) == 0:
            j += 1
            continue
        cur = dp[j][cur]
        Y -= (1 << j)
        j += 1
    print(cur+1)
