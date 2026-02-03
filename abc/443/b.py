N, K = map(int, input().split())

now = N * (N - 1) // 2

lo, hi = 0, K
while hi - lo > 1:
    mi = (lo + hi) // 2
    additional = mi * (mi + 1) // 2 - now

    if additional >= K:
        hi = mi
    else:
        lo = mi
print(max(0, lo - N + 1))
