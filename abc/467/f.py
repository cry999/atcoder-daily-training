import sys
from atcoder.segtree import SegTree

input = sys.stdin.readline

N, Q = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

queries = []
all_b = set(B)

for _ in range(Q):
    q, i, x = map(int, input().split())
    i -= 1

    queries.append((q, i, x))
    if q == 2:
        all_b.add(x)

sorted_b = sorted(all_b, reverse=True)

# B の値 -> SegTree 上の添字
index_b = {b: i for i, b in enumerate(sorted_b)}

M = len(sorted_b)

# 同じ b に対する a の合計
sum_a_by_b = [0] * M
for a, b in zip(A, B):
    sum_a_by_b[index_b[b]] += a

# SegTree 上のノードは (ここまでの A の合計, max(ここまでの A の合計 + B))
# で管理する。


def op(left: tuple[int, int], right: tuple[int, int]):
    sum_l, ans_l = left
    sum_r, ans_r = right
    return (
        sum_l + sum_r,
        max(ans_l, sum_l + ans_r),
    )


E = (0, 0)


def node(i: int):
    """
    i: index_b[B] の値
    """
    sum_a = sum_a_by_b[i]
    if not sum_a:
        return E
    return (sum_a, sum_a + sorted_b[i])


seg = SegTree(op=op, e=E, v=[node(i) for i in range(M)])

ans = [0] * Q
for q, (t, i, x) in enumerate(queries):
    if t == 1:
        p = index_b[B[i]]

        sum_a_by_b[p] += x - A[i]
        A[i] = x

        seg.set(p, node(p))

    else:
        old = index_b[B[i]]
        new = index_b[x]

        if old != new:  # 更新が必要な時だけやる
            # 古い B を一旦取り除く
            sum_a_by_b[old] -= A[i]
            seg.set(old, node(old))

            # 新しい B を加える
            sum_a_by_b[new] += A[i]
            seg.set(new, node(new))

            B[i] = x

    ans[q] = seg.all_prod()[1]

print("\n".join(map(str, ans)))
