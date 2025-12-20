from collections import defaultdict


N = int(input())
*A, = map(int, input().split())

hist = defaultdict(list)
for i, a in enumerate(A):
    hist[a].append(i)

ans = float('inf')
for k, v in hist.items():
    if len(v) == 1:
        continue
    for i in range(len(v)-1):
        ans = min(ans, v[i+1]-v[i]+1)
print(ans if ans < float('inf') else -1)
