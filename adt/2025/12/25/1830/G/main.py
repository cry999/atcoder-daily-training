from sortedcontainers import SortedSet


N, K = map(int, input().split())
*P, = map(int, input().split())
rev_p = [-1] * (N+1)
for i in range(N):
    rev_p[P[i]] = i

s = SortedSet()
for k in range(1, K+1):
    s.add(rev_p[k])

ans: int = s[-1]-s[0]

for i in range(1, N-K+1):
    s.remove(rev_p[i])
    s.add(rev_p[i+K])
    ans = min(ans, s[-1]-s[0])
    if ans == 0:
        break

print(ans)
