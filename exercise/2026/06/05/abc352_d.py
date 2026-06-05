from sortedcontainers import SortedList

N, K = map(int, input().split())
(*P,) = map(int, input().split())

rev = [-1] * (N + 1)
for i in range(N):
    rev[P[i]] = i

q = SortedList()
for i in range(K - 1):
    q.add(rev[i + 1])

ans = float("inf")
for i in range(K, N + 1):
    q.add(rev[i])
    ans = min(ans, q[-1] - q[0])
    q.remove(rev[i - K + 1])

print(ans)
