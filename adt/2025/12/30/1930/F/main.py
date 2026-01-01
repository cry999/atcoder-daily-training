from collections import defaultdict


N = int(input())
(*A,) = map(int, input().split())

hist = defaultdict(int)
for a in A:
    hist[a] += 1

ans = 0
for v in hist.values():
    ans += v // 2
print(ans)
