from atcoder.segtree import SegTree

N, M = map(int, input().split())
(*P,) = map(int, input().split())

min_tree = SegTree(min, float("inf"), P)
max_tree = SegTree(max, float("-inf"), P)
rev_p = [0] * (N + 1)
for i in range(N):
    rev_p[P[i]] = i

for _ in range(M):
    l, r = map(int, input().split())

    min_v = min_tree.prod(l - 1, r)
    max_v = max_tree.prod(l - 1, r)

    i = rev_p[min_v]
    j = rev_p[max_v]

    min_tree.set(i, max_v)
    min_tree.set(j, min_v)

    max_tree.set(i, max_v)
    max_tree.set(j, min_v)

    rev_p[min_v], rev_p[max_v] = j, i

ans = [0] * N
for i in range(N):
    ans[rev_p[i + 1]] = i + 1
print(*ans)
