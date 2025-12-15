from collections import defaultdict
import heapq


N = int(input())

# 同じ味の組み合わせは、おいしさ TOP2 だけ考えれば良い。
# 異なる味の組み合わせは、味ごとに TOP1 を選出して、そのうちの最大 2 つで良い。

same_flavor = defaultdict(list)
top_flavors = []

for _ in range(N):
    F, S = map(int, input().split())
    heapq.heappush(same_flavor[F], -S)
    heapq.heappush(top_flavors, (-S, F))

ans = 0
for ss in same_flavor.values():
    if len(ss) < 2:
        continue

    s, t = heapq.heappop(ss), heapq.heappop(ss)
    s, t = -s, -t
    ans = max(ans, s+t//2)

s, f = heapq.heappop(top_flavors)
s = -s
# print(top_flavors)

for _ in range(N-1):
    si, fi = heapq.heappop(top_flavors)
    si = -si
    # print(f, s, fi, si)
    if f == fi:
        continue
    ans = max(ans, s+si)

print(ans)
