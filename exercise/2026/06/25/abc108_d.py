L = int(input())

N = 20
edges = []
for i in range(1, N):
    edges.append((i, i + 1, 0))

pow2 = 2
exp = 1
while pow2 <= L:
    edges.append((exp, exp + 1, pow2 // 2))
    if L & (1 << (exp - 1)):
        edges.append((exp, N, L & ~((1 << exp) - 1)))
    pow2 *= 2
    exp += 1

print(N, len(edges))
for u, v, w in edges:
    print(u, v, w)
