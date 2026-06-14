from math import isqrt

N = int(input())

# kernel[n] = n から平方数をのぞいた数
kernel = list(range(N + 1))

for p in range(2, isqrt(N) + 1):
    pp = p * p
    # pp の倍数から pp を取り除く
    for k in range(pp, N + 1, pp):
        while kernel[k] % pp == 0:
            kernel[k] //= pp

# kernel[i] == kernel[j] となる (i, j) の組み合わせの個数を求める
cnt = [0] * (N + 1)
for k in range(1, N + 1):
    cnt[kernel[k]] += 1

print(sum(c * c for c in cnt))
