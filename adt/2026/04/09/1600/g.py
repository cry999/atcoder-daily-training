N = int(input())
intervals = sorted(tuple(map(int, input().split())) for _ in range(N))

ans = 0
for i in range(N - 1):
    l, r = intervals[i]

    lo, hi = i, N
    while hi - lo > 1:
        mi = (lo + hi) // 2
        ml, mr = intervals[mi]

        if ml <= r:
            lo = mi
        else:
            hi = mi

    ans += lo - i

print(ans)
