from collections import defaultdict


N = int(input())
(*A,) = map(int, input().split())

hist = defaultdict(int)
for a in A:
    hist[a] += 1

sorted_a = sorted(hist.items(), reverse=True)

for k in range(N):
    if k < len(sorted_a):
        print(sorted_a[k][1])
    else:
        print(0)
