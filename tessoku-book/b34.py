# MAX_A = 100
# X, Y = 4, 2
#
# # 実験。周期 5 で dp が決まる。
#
# dp = [0] * (MAX_A+1)
# for i in range(MAX_A+1):
#     min_num = [False]*3
#     if i >= X:
#         min_num[dp[i-X]] = True
#     if i >= Y:
#         min_num[dp[i-Y]] = True
#
#     if not min_num[0]:
#         dp[i] = 0
#     elif not min_num[1]:
#         dp[i] = 1
#     else:
#         dp[i] = 2
#
#
# N = X + Y
# for i in range(MAX_A//N):
#     print(i, dp[i*N:(i+1)*N])
#
from functools import reduce as r

N, X, Y = map(int, input().split())
A = list(map(int, input().split()))
dp = [0] * (X+Y)
for i in range(X+Y):
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

print(r(
    lambda x, y: x ^ y,
    map(lambda a: dp[a % (X+Y)], A)
) != 0 and 'First' or 'Second')
