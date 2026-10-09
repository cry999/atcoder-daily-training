# >>> atcoder-stat >>>
# started_at  = 2026-10-09T09:08:53+09:00
# solved_at   = 2026-10-09T09:51:26+09:00
# duration_ms = 2553236
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
from atcoder.dsu import DSU

N, Q = map(int, input().split())

# dsu[k] := 辺の重みが k 以下の辺だけで構成される DSU
dsu = [DSU(N) for _ in range(10)]

ans = 0
for i in range(N - 1):
    a, b, c = map(int, input().split())
    a -= 1
    b -= 1
    ans += c

    for k in range(c, 10):
        dsu[k].merge(a, b)


# 考察
# 1. 最初の状態は MST
# 2. クエリの辺を追加するかどうか。
# 3. 与えられた時に必要ないなら、その後も必要にはならない。
# なぜなら、u, v を繋ぐのにもっと効率的な繋ぎ方があるということだから
# 4. クエリの辺を使いする場合. a: すでに (u, v) を繋ぐ辺が採用されている or b: (u, v) を繋ぐ辺を追加するとループができる
# 4.a. 置き換えるだけ
# 4.b. ループの中で最も重い辺を削除する。これは LCA を利用する？

# TODO: 辺の交換に対応する仕組みと、各クエリの MST 重みの出力。
for _ in range(Q):
    u, v, w = map(int, input().split())
    u -= 1
    v -= 1

    for k in range(w, 10):
        if dsu[k].same(u, v):
            # k 以下の辺だけですでに連結なら、それ以上の重みの辺を利用した場合は当然連結
            break
        dsu[k].merge(u, v)
        ans -= 1

    print(ans)
