from collections import defaultdict
from sortedcontainers import SortedList

N = int(input())
(*A,) = map(int, input().split())

hist = defaultdict(SortedList)
for i, a in enumerate(A):
    hist[a].add(i)

ans = 0
for j, a in enumerate(A):
    if a % 5:
        continue
    ai = a // 5 * 7
    ak = a // 5 * 3

    if ai not in hist or ak not in hist:
        continue
    ii = hist[ai].bisect_left(j)
    kk = hist[ak].bisect_left(j)

    ans += ii * kk
    ans += (len(hist[ai]) - ii) * (len(hist[ak]) - kk)
print(ans)
