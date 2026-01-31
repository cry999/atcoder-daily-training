N, K = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

# dp[i][0/1] := i 番目の A or B (0 or 1) を選択できるか？
dp = [[False] * 2 for _ in range(N)]
dp[0] = [True, True]

for i in range(N - 1):
    a1, b1 = A[i], B[i]
    a2, b2 = A[i + 1], B[i + 1]

    dp[i + 1][0] = (dp[i][0] and abs(a2 - a1) <= K) or (dp[i][1] and abs(a2 - b1) <= K)
    dp[i + 1][1] = (dp[i][0] and abs(b2 - a1) <= K) or (dp[i][1] and abs(b2 - b1) <= K)

if any(dp[-1]):
    print("Yes")
else:
    print("No")
