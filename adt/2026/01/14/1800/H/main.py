N, M = map(int, input().split())
(*A,) = map(int, input().split())

graph = [[] for _ in range(N)]
initial_costs = [0] * N
for _ in range(M):
    u, v = map(int, input().split())
    graph[u - 1].append(v - 1)
    graph[v - 1].append(u - 1)

    initial_costs[u - 1] += A[v - 1]
    initial_costs[v - 1] += A[u - 1]

lo, hi = -1, max(A) * N
while hi - lo > 1:
    mi = (lo + hi) // 2
    # mi 以下のコストで N 回の操作を達成できるか？

    # 初期化
    stack = []
    deleted = [False] * N
    costs = initial_costs[:]
    for i in range(N):
        if costs[i] <= mi:
            stack.append(i)
            deleted[i] = True

    while stack:
        i = stack.pop()
        for j in graph[i]:
            # 削除した影響を伝播させる
            costs[j] -= A[i]
            if costs[j] <= mi and not deleted[j]:
                stack.append(j)
                deleted[j] = True

    if all(deleted):
        hi = mi
    else:
        lo = mi
print(hi)
