# >>> atcoder-stat >>>
# started_at  = 2026-07-20T10:45:22+09:00
# solved_at   = 2026-07-20T11:35:47+09:00
# duration_ms = 1500000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys
from atcoder.segtree import SegTree

input = sys.stdin.readline

N = int(input())

boxes = []
# w を segtree 上の index として利用するために座標圧縮したいので set でもつ。
w_set: set[int] = set()
for _ in range(N):
    # h <= w <= d となるようにする
    h, w, d = sorted(map(int, input().split()))
    w_set.add(w)
    boxes.append((h, w, d))

boxes.sort()
w_index = {w: i for i, w in enumerate(sorted(w_set))}


# 処理ずみ h に対して、w 未満の最小の d を管理する SegTree を構築する。
# 区間最小値を取得できるようにする。


def op(left: int, right: int):
    return min(left, right)


INF = 10**18
seg = SegTree(op=op, e=INF, v=[INF] * N)

prev_h = 0
# 同じ h に対して、(w, d) の一時退避場所
stack = []
for h, w, d in boxes:
    if prev_h != h:
        # h が異なるなら stack を seg に反映させる。
        while stack:
            w0, d0 = stack.pop()
            i = w_index[w0]
            seg.set(i, min(d0, seg.get(i)))

    i = w_index[w]
    if seg.prod(0, i) < d:
        print("Yes")
        break

    # 一旦 stack に退避して、次の h が今の h と異なるなら seg
    # に反映させる。
    stack.append((w, d))
    prev_h = h
else:
    print("No")
