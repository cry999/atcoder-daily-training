from collections import defaultdict


N, M, K = map(int, input().split())
edges = [tuple(map(lambda x: int(x), input().split())) for _ in range(M)]
*E, = map(lambda x: int(x)-1, input().split())
# print(edges)

g = [defaultdict(int) for _ in range(N+1)]
dp = [float('inf')]*(N+1)
dp[1] = 0

for i, e in enumerate(E):
    a, b, c = edges[e]
    # print(f'{i=}, {e=}, {a=}, {b=}, {c=}')
    dp[b] = min(
        dp[b],
        dp[a] + c,
    )
    # print(*dp)

print(dp[-1] if dp[-1] < float('inf') else -1)
