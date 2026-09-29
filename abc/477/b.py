from collections import defaultdict

N, D = map(int, input().split())
(*X,) = map(int, input().split())

counter = defaultdict(list)
for i, x in enumerate(X):
    counter[x].append(i)

ordered = sorted(counter.items(), key=lambda x: x[0])
M = len(ordered)
ans = []
for i in range(M):
    x, a = ordered[i]
    if len(a) > 1:
        continue

    if i > 0:
        p, _ = ordered[i - 1]
        if x - p < D:
            continue
    if i < M - 1:
        n, _ = ordered[i + 1]
        if n - x < D:
            continue

    ans.append(a[0] + 1)

ans.sort()
print(len(ans))
print(*ans)
