from bisect import bisect_right
import math

N, M, K = map(int, input().split())
X, Y = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

A.sort()
B.sort()

# n このデザートを買うために必要な資金
prefix_dessert = [0] * (N + 1)
for i in range(N):
    prefix_dessert[i + 1] = prefix_dessert[i] + A[i]

ans = bisect_right(prefix_dessert, X + K * Y) - 1  # デザートだけ買う場合の最大個数

changes = 0  # ドリンクを買ったお釣り
rest_k_dollar = Y
for num_drink in range(1, M + 1):
    # n 枚の K ドル紙幣が必要
    n = math.ceil(B[num_drink - 1] / K)
    if n > rest_k_dollar:
        break
    rest_k_dollar -= n
    changes += n * K - B[num_drink - 1]
    use_for_dessert = X + rest_k_dollar * K + changes
    num_dessert = bisect_right(prefix_dessert, use_for_dessert) - 1
    ans = max(ans, num_drink + num_dessert)
print(ans)
