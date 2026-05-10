from collections import defaultdict

N, M = map(int, input().split())

l2r = [[] for _ in range(N + 1)]
r2l = [[] for _ in range(N + 1)]
cnt = defaultdict(int)

min_r_at_l = [N + 1] * (N + 1)

for i in range(M):
    l, r = map(int, input().split())
    l2r[l].append(r)
    r2l[r].append(l)
    cnt[(l, r)] += 1
    min_r_at_l[l] = min(min_r_at_l[l], r)

for i in range(N + 1):
    l2r[i].sort()
    r2l[i].sort(reverse=True)

for i in range(N - 1, -1, -1):
    min_r_at_l[i] = min(min_r_at_l[i], min_r_at_l[i + 1])

Q = int(input())
for _ in range(Q):
    S, T = map(int, input().split())

    if not l2r[S] or not r2l[T]:
        print("No")
        continue

    if cnt[(S, T)] > 0:
        if cnt[(S, T)] >= 2:
            print("Yes")
        elif S + 1 <= N and min_r_at_l[S + 1] <= T:
            print("Yes")
        elif min_r_at_l[S] <= T - 1:
            print("Yes")
        else:
            print("No")
        continue

    # l = S で r <= T を満たす最大の r を探す
    lo, hi = 0, len(l2r[S])
    while hi - lo > 1:
        mi = (lo + hi) // 2
        if l2r[S][mi] <= T:
            lo = mi
        else:
            hi = mi

    if l2r[S][lo] > T:
        print("No")
        continue

    r = l2r[S][lo]

    # r = T で l >= S を満たす最小の l を探す
    lo, hi = 0, len(r2l[T])
    while hi - lo > 1:
        mi = (lo + hi) // 2
        if S <= r2l[T][mi]:
            lo = mi
        else:
            hi = mi

    if r2l[T][lo] < S:
        print("No")
        continue

    l = r2l[T][lo]

    if l <= r + 1:
        print("Yes")
    else:
        print("No")
