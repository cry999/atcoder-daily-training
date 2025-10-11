N, M = map(int, input().split())
edges = {}

for _ in range(M):
    A, B = map(int, input().split())
    edges.setdefault(A, []).append(B)
    edges.setdefault(B, []).append(A)

for k in range(1, N+1):
    print(f'{k}: {{{", ".join(str(i) for i in edges[k])}}}')
