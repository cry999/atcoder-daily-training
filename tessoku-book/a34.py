from functools import reduce as r


N, X, Y = map(int, input().split())
A = list(map(int, input().split()))
MAX_A = max(A)

dp = [0] * (MAX_A+1)
for i in range(MAX_A+1):
    min_num = [False]*3
    if i >= X:
        min_num[dp[i-X]] = True
    if i >= Y:
        min_num[dp[i-Y]] = True

    if not min_num[0]:
        dp[i] = 0
    elif not min_num[1]:
        dp[i] = 1
    else:
        dp[i] = 2

print(r(lambda x, y: x ^ y, map(
    lambda a: dp[a], A,
)) != 0 and 'First' or 'Second')
