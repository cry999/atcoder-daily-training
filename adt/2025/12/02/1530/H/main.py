# ref: https://hackmd.io/@tatyam-prime/H1EhuQAt1x

N, K = map(int, input().split())
*A, = map(int, input().split())

# 愚直方法
# from math import gcd
# from itertools import combinations
#
# max_gcd = {}
# for combination in combinations(range(N), K):
#     # print(combination)
#     i0, i1 = combination[0], combination[1]
#     g = gcd(A[i0], A[i1])
#     for i in combination[2:]:
#         g = gcd(g, A[i])
#         if g == 1:
#             break
#     for i in combination:
#         max_gcd[i] = max(max_gcd.get(i, 0), g)
#
# for i in range(N):
#     print(max_gcd[i])

MAX_A = max(A)

primes = []
factor = [1] * (MAX_A + 1)
for i in range(2, MAX_A+1):
    if factor[i] == 1:
        primes.append(i)
        factor[i] = i
    for p in primes:
        if i*p > MAX_A or p > factor[i]:
            break
        factor[i*p] = p

# cnt[x] = x の倍数の個数
cnt = [0] * (MAX_A+1)
for a in A:
    cnt[a] += 1

# 約数方向に累積和をとっていく
for p in primes:
    for i in range(MAX_A//p, 0, -1):
        cnt[i] += cnt[i*p]

# A[i] の約数 d のなかで cnt[d] >= K を満たす最大の d を探す
# ans[d] = d の約数の中で cnt[d] >= K を満たす最大の約数
ans = [0] * (MAX_A+1)

# まずは自分自身をセット
for i in range(MAX_A+1):
    if cnt[i] >= K:
        ans[i] = i
# 次に倍数方向に伝搬させていく
for p in primes:
    for i in range(1, MAX_A//p+1):
        ans[i*p] = max(ans[i*p], ans[i])

# 答えを出力
for a in A:
    print(ans[a])
