from math import gcd

N, M, K = map(int, input().split())

G = gcd(N, M)
n, m = N // G, M // G
L = n * m * G

# N の倍数であって、M の倍数でないものは、
# Lx + N, Lx + 2N, ..., Lx + (m-1)N
# 逆に、M の倍数であって、 N の倍数でないものは、
# Lx + M, Lx + 2M, ..., Lx + (n-1)M
# x を求めて、その後に +α を求める。
# +α 部分は二分探索でいけそう。
x, r = divmod(K, n + m - 2)
# print(f"{x=}, {r=}")
if r == 0:
    print(x * L - min(N, M))
else:
    # X 以下の値が r 個になるような X の最小値を探す
    lo, hi = 0, L
    while hi - lo > 1:
        mi = (lo + hi) // 2
        num_m = mi // M
        num_n = mi // N

        # print(f"{lo=}, {hi=}, {mi=}, {num_m=}, {num_n=}")

        if num_m + num_n < r:
            lo = mi
        else:
            hi = mi

    print(x * L + hi)
