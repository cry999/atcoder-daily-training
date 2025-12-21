import heapq
import os
import sys

DEBUG = os.getenv('DEBUG', '0') == '1'


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs, file=sys.stderr)


N, M, K = map(int, input().split())

g = [[] for _ in range(2*N)]

for i in range(M):
    u, v, a = map(int, input().split())
    u, v = u-1, v-1
    nu, nv = u+N, v+N  # スイッチを推した世界線の u と v
    # スイッチを押すことで世界を移動可能
    if a:
        # スイッチ推した回数が偶数回だと元の世界線で通行可能
        g[u].append((v, 1)), g[v].append((u, 1))
    else:
        # スイッチ押した回数が奇数回だと並行世界で通行可能
        g[nu].append((nv, 1)), g[nv].append((nu, 1))

*S, = map(int, input().split())
for s in S:
    s -= 1  # スイッチのある頂点
    ns = s+N  # 並行世界の頂点 s
    g[s].append((ns, 0)), g[ns].append((s, 0))

queue = [(0, 0)]  # (コスト, 頂点)
min_costs = [float('inf')] * (2*N)
while queue:
    cost, u = heapq.heappop(queue)
    debug(f'u={u % N}(switch={u//N}), {cost=}')
    if min_costs[u] <= cost:
        continue
    min_costs[u] = cost

    for v, dcost in g[u]:
        ncost = cost+dcost
        if min_costs[v] <= ncost:
            continue
        queue.append((ncost, v))
ans = min(min_costs[N-1], min_costs[2*N-1])
if ans == float('inf'):
    print(-1)
else:
    print(ans)
