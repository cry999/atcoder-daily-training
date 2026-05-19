from collections import deque

N, K = map(int, input().split())
(*A,) = map(lambda x: int(x) % K, input().split())

A.sort()

q = deque(A)
ans = q[-1] - q[0]
for _ in range(N):
    a = q.popleft()
    q.append(a + K)
    ans = min(ans, q[-1] - q[0])

print(ans)
