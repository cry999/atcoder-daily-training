# >>> atcoder-stat >>>
# started_at  = 2026-09-27T10:05:08+09:00
# solved_at   = 2026-09-27T10:11:19+09:00
# duration_ms = 371791
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import heapq
import sys

input = sys.stdin.readline

N, Q = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

prefix = [0] * (N + 1)
for i in range(N):
    prefix[i + 1] = prefix[i] + A[i]

dist = B.copy()
q = [(dist[i], i) for i in range(N)]
heapq.heapify(q)

while q:
    c, u = heapq.heappop(q)
    if c != dist[u]:
        # 最短経路じゃなくなっているのでスキップ
        continue

    for v, w in [
        ((u + 1) % N, A[u]),  # u -> u+1
        ((u - 1) % N, A[(u - 1) % N]),  # u -> u-1
    ]:
        nc = c + w
        if nc < dist[v]:
            dist[v] = nc
            heapq.heappush(q, (nc, v))

# dist[i] := 0 から i までの最短距離が出来上がっている。
for _ in range(Q):
    s, t = map(int, input().split())
    s, t = s - 1, t - 1

    if s == t:
        print(0)
        continue
    if s == N:
        print(dist[t])
        continue
    if t == N:
        print(dist[s])
        continue

    d = abs(prefix[t] - prefix[s])
    ans = min(
        d,
        prefix[N] - d,
        dist[s] + dist[t],
    )
    print(ans)
