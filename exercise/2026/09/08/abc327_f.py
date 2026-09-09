# >>> atcoder-stat >>>
# started_at  = 2026-09-08T16:15:39+09:00
# <<< atcoder-stat <<<
import sys
from atcoder.lazysegtree import LazySegTree

input = sys.stdin.readline


# 時刻 T[i] に座標 X[i] にりんごが落ちてくる。
# 以下の 2 条件を満たすりんごを最大化する。変数は S と L。
# 1. 時刻 [S, S+D) の期間に落ちる
# 2. 座標 [L, L+W) の範囲に落ちる
# それぞれ単一の条件なら単純なイベント処理でできる。
# 気づき
# 1. 時刻 T[i] にカゴをおくことを考慮する必要があるのは X[i] の周囲だけ
# 2. 具体的には、L が X[i]-W+1 から X[i] の範囲
# 3. 落ちる時刻だけが重要。範囲外になる時間は最大値を更新しない。
# LazySegTree で区間加算と区間最大値を取れば良い?

N, D, W = map(int, input().split())
events = []
max_x = 0
for _ in range(N):
    t, x = map(int, input().split())
    events.append((t, x, +1))  # 落ちる瞬間
    events.append((t + D, x, -1))  # 対象外になる時間
    max_x = max(max_x, x)
events.sort()


def op(left: int, right: int):
    return max(left, right)


def mapping(f: int, value: int):
    return f + value


def composition(f: int, g: int):
    return f + g


INF = 10**18

e = -INF
id_ = 0


seg = LazySegTree(op, e, mapping, composition, id_, [0] * (max_x + 1))

i = 0
ans = 0
while i < 2 * N:
    t, r, delta = events[i]
    l = max(0, r - W + 1)
    seg.apply(l, r + 1, delta)
    while i + 1 < 2 * N and events[i + 1][0] == t:
        _, r, delta = events[i + 1]
        l = max(0, r - W + 1)
        seg.apply(l, r + 1, delta)
        i += 1
    ans = max(ans, seg.all_prod())
    i += 1
print(ans)
