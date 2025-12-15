import heapq


N, M = map(int, input().split())
*A, = map(int, input().split())

g = [[] for _ in range(N)]


for _ in range(M):
    u, v = map(int, input().split())
    u, v = u-1, v-1

    if A[u] == A[v]:
        g[u].append((v, 0))
        g[v].append((u, 0))
    else:
        if A[u] < A[v]:
            u, v = v, u
        g[v].append((u, 1))

queue = [(A[0], 0, -1)]
score = [0]*N
# print(f'{g=}')
while queue:
    # print(f'{score=}')
    _, v, s = queue.pop()
    s = -s
    if score[v] > s:
        # print(f'skip {v} {s}')
        continue
    score[v] = s

    for nv, ns in g[v]:
        if score[nv] >= s+ns:
            # print(f'skip {nv=} {ns=}')
            continue
        score[nv] = s+ns
        heapq.heappush(queue, (A[nv], nv, -s-ns))

print(score[-1])
