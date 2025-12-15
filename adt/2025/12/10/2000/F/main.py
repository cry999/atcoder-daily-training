from collections import defaultdict


N = int(input())
*A, = map(int, input().split())

hist = defaultdict(int)
for a in A:
    hist[a] += 1

ans = sum(v*(v-1)//2 * (N-v) for v in hist.values())
print(ans)
