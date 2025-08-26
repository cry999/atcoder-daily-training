N = int(input())
A = list(map(int, input().split()))
# 自分の考えた解放
# B = [0] * N
#
# for i in range(N):
#     # i: start
#     c = 0
#     for j in range(N-i):
#         # j: 連続する区画の数
#         c += A[i+j]
#         # print(i, j, c)
#         B[j] = max(B[j], c)
#
# 累積和を使う解放
B = [0] * (N+1)
# B[i] を 1区画目からi区画目までの合計値とする。
# この場合、j区画目からk個の連続した区間の合計値は B[j+k]-B[j-1] で表現される。
# なので、k個の連続した区間の最大値は max(B[j+k]-B[j-1] for j in range(N-k)) となる。
for i in range(N):
    B[i+1] = B[i] + A[i]

for k in range(1, N+1):
    print(max(B[j+k]-B[j] for j in range(N-k+1)))
