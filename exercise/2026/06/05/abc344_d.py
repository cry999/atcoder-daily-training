T = input()
N = int(input())

dp = [[float("inf")] * (len(T) + 1) for _ in range(N + 1)]
dp[0][0] = 0

for i in range(N):
    _, *S = input().split()

    for j in range(len(T)):
        for k, s in enumerate(S):
            if dp[i][j] == float("inf"):
                continue
            dp[i + 1][j] = min(dp[i + 1][j], dp[i][j])

            if not T[j:].startswith(s):
                continue
            dp[i + 1][j + len(s)] = min(
                dp[i + 1][j + len(s)],
                dp[i][j] + 1,
            )
    dp[i + 1][len(T)] = min(dp[i + 1][len(T)], dp[i][len(T)])

# print(dp)
ans = dp[N][len(T)]
if ans == float("inf"):
    print(-1)
else:
    print(ans)
