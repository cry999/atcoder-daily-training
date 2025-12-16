from itertools import permutations


N, M = map(int, input().split())

edges = set()


def edge(u: int, v: int) -> tuple[int, int]:
    return (min(u, v), max(u, v))


for _ in range(M):
    u, v = map(int, input().split())
    edges.add(edge(u, v))

# 連結成分が 1 つの場合
ans = float('inf')
for perm in permutations(range(1, N+1), N):
    ok_edges = set()
    for i in range(N):
        ok_edges.add(edge(perm[i-1], perm[i]))

    ans = min(ans, len(edges.difference(ok_edges)) +
              len(ok_edges.difference(edges)))

# 連結成分が複数( 2 つ)の場合
for perm in permutations(range(1, N+1), N):
    for L1, L2 in [(3, N-3), (4, N-4)]:
        if L1 > L2:
            break
        perm1, perm2 = perm[:L1], perm[L1:]

        ok_edges = set()
        for i in range(L1):
            ok_edges.add(edge(perm1[i-1], perm1[i]))
        for i in range(L2):
            ok_edges.add(edge(perm2[i-1], perm2[i]))

        ans = min(ans, len(edges.difference(ok_edges)) +
                  len(ok_edges.difference(edges)))
print(ans)
