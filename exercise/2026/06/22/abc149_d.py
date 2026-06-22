N, K = map(int, input().split())
R, S, P = map(int, input().split())
T = input()

# 0: 👊, 1: ✌️, 2: 🖐️
dp = [[0] * 3 for _ in range(N + 1)]

for i in range(1, N + 1):
    if T[i - 1] == "r":
        dp[i][2] = P
    elif T[i - 1] == "s":
        dp[i][0] = R
    else:
        dp[i][1] = S

    if i - K > 0:
        dp[i][0] += max(dp[i - K][1], dp[i - K][2])
        dp[i][1] += max(dp[i - K][0], dp[i - K][2])
        dp[i][2] += max(dp[i - K][0], dp[i - K][1])

print(sum(max(dp[N - k]) for k in range(K)))
