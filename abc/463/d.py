N, K = map(int, input().split())

clothes = [tuple(map(int, input().split())) for _ in range(N)]
clothes.sort(key=lambda x: x[1])

lo, hi = 0, 10**9
while hi - lo > 1:
    mi = (lo + hi) // 2
    cur_r = -float("inf")
    k = 0
    for l, r in clothes:
        if l - cur_r < mi:
            continue
        cur_r = r
        k += 1

    if k >= K:
        lo = mi
    else:
        hi = mi

if lo == 0:
    print(-1)
else:
    print(lo)
