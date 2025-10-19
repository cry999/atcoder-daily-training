N, M = map(int, input().split())
edges = [[] for _ in range(N+1)]

for _ in range(M):
    A, B = map(int, input().split())
    edges[A].append(B)
    edges[B].append(A)

for k in range(1, N+1):
    print(f'{k}: {{{", ".join(str(i) for i in edges[k])}}}')
