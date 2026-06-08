N = int(input())
(*A,) = map(int, input().split())

M = int(input())
(*B,) = map(int, input().split())

X = int(input())

dp = [0] * (X + 1)
dp[0] = 1
for b in B:
    dp[b] = -1

for i in range(X):
    for a in A:
        if i + a <= X and dp[i + a] != -1 and dp[i] != -1:
            dp[i + a] = max(dp[i + a], dp[i])

print("Yes" if dp[X] == 1 else "No")
