N = int(input())
S = list(map(int, input().split()))
T = list(map(int, input().split()))

# dp[i]: i 番目のすぬけくんが宝石をもらう最小時刻
dp = [float('inf')] * (N)

for i in range(N):
    dp[(i+1) % N] = min(dp[i] + S[i], T[(i+1) % N])
for i in range(N):
    dp[(i+1) % N] = min(dp[i] + S[i], T[(i+1) % N])

for i in range(N):
    print(dp[i])
