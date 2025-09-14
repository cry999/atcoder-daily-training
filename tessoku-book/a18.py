N, S = map(int, input().split())
A = list(map(int, input().split()))

dp = [[False] * (S+1) for _ in range(N+1)]
dp[0][0] = True

# i 枚目までのカードを利用して、合計 j を作れるか？
for i in range(N):
    for j in range(S+1):
        if j - A[i] >= 0:
            dp[i+1][j] = dp[i][j] or dp[i][j-A[i]]
        else:
            dp[i+1][j] = dp[i][j]

print('Yes' if dp[N][S] else 'No')
# for row in dp:
#     for cell in row:
#         print('T' if cell else 'F', end=' ')
#     print()
# for i in range(S+1):
#     print(f'{i:1}', end=' ')
# print()
