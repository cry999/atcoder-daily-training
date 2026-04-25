N, K = map(int, input().split())
(*A,) = map(int, input().split())

hist = {}
for a in A:
    hist[a] = hist.get(a, 0) + 1

rank = sorted(k * v for k, v in hist.items())
ans = sum(rank[:-K])
print(ans)
