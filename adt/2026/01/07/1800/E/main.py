from itertools import permutations

N = int(input())

MG = int(input())
g = [set() for _ in range(N)]
for _ in range(MG):
    u, v = map(int, input().split())
    u, v = u - 1, v - 1
    g[u].add(v)
    g[v].add(u)

MH = int(input())
h = [set() for _ in range(N)]
for _ in range(MH):
    a, b = map(int, input().split())
    a, b = a - 1, b - 1
    h[a].add(b)
    h[b].add(a)

A = [[0] * N for _ in range(N)]
for i in range(N - 1):
    (*a,) = map(int, input().split())
    for j in range(i):
        A[i][j] = A[j][i]
    A[i][i] = 0
    for j, v in enumerate(a):
        A[i][i + j + 1] = v
for i in range(N - 1):
    A[-1][i] = A[i][-1]

# 実装の要は2点
# 1. G と H の頂点をどう対応させるか
# 2. 確定した二つのグラフを同型にするための辺の操作のコストをどう見積もるか


def operation_cost(g_to_h: map, h_to_g: map) -> int:
    checked = [[False] * N for _ in range(N)]
    cost = 0
    # print(f"check: {g_to_h}")

    for u in range(N):
        a = g_to_h[u]
        for v in g[u]:
            b = g_to_h[v]
            ma, mb = min(a, b), max(a, b)
            if checked[ma][mb]:
                continue
            checked[ma][mb] = True
            if b not in h[a]:
                # print(f"  append edge ({a}, {b})")
                cost += A[a][b]

    for a in range(N):
        u = h_to_g[a]
        for b in h[a]:
            ma, mb = min(a, b), max(a, b)
            if checked[ma][mb]:
                continue
            checked[ma][mb] = True

            v = h_to_g[b]

            if v not in g[u]:
                # print(f"  remove edge ({a}, {b})")
                cost += A[a][b]

    # print(f"  {cost=}")
    return cost


ans = float("inf")
for perm in permutations(range(N)):
    g_to_h = {}
    h_to_g = {}
    for i, p in enumerate(perm):
        g_to_h[i] = p
        h_to_g[p] = i
    ans = min(ans, operation_cost(g_to_h, h_to_g))
print(ans)
