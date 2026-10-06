import sys

input = sys.stdin.readline


N, Q = map(int, input().split())
queries = [[] for _ in range(Q + 1)]
for _ in range(Q):
    l, r, x = map(int, input().split())
    queries[x].append((l - 1, r))

ans = [0] * (N + 1)

for x in range(1, Q + 1):
    if not queries[x]:
        continue
    queries[x].sort()
    l0, r0 = queries[x][0]

    for l, r in queries[x]:
        if l0 <= l <= r0:
            r0 = max(r0, r)
        else:
            ans[l0] += 1
            ans[r0] -= 1
            l0, r0 = l, r
    ans[l0] += 1
    ans[r0] -= 1

for i in range(1, N + 1):
    ans[i] += ans[i - 1]

print(*ans[:N])
