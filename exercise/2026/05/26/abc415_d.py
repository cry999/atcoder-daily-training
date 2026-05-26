from sortedcontainers import SortedList

N, M = map(int, input().split())

s = SortedList()
for _ in range(M):
    a, b = map(int, input().split())
    s.add((a - b, a))


ans = 0
while s:
    while s and s[0][1] > N:
        s.pop(0)

    if not s:
        break

    d, a = s.pop(0)
    # print(f"{d=}, {a=}, {N=}")

    lo, hi = 0, N // d + 1
    while hi - lo > 1:
        mi = (lo + hi) // 2
        if N - mi * d >= a:
            lo = mi
        else:
            hi = mi

    # print(f"  {lo=}, {hi=}")
    N -= (lo + 1) * d
    # print(f"  {N=}")
    ans += lo + 1

print(ans)
