# >>> atcoder-stat >>>
# started_at  = 2026-07-10T08:56:53+09:00
# solved_at   = 2026-07-10T08:57:02+09:00
# duration_ms = 1200000
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 2
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline

MOD = 10**9 + 7

N = int(input())
g = [[] for _ in range(N + 1)]
for _ in range(N - 1):
    a, b = map(int, input().split())
    g[a].append(b)
    g[b].append(a)


# 1 を根として BFS で各頂点の親を求める。
parent = [-1] * (N + 1)
order = [1]
for u in order:
    for v in g[u]:
        if v == parent[u]:
            continue

        parent[v] = u
        order.append(v)

# size[v] := v を根とする部分木のサイズ (頂点数)
size = [1] * (N + 1)
# order の逆順にすることで、葉の方からサイズを決定して DFS っぽいことができる
for v in reversed(order[1:]):
    # v を根とする部分木のサイズを親に足すことで、親を根とする
    # 部分木のサイズを求めることができる。
    size[parent[v]] += size[v]

# 1 / 2 % MOD
inv2 = pow(2, MOD - 2, MOD)
# inv_pow2[i] := 2^(-i) % MOD
inv_pow2 = [1] * (N + 1)
for i in range(1, N + 1):
    inv_pow2[i] = (inv_pow2[i - 1] * inv2) % MOD

# ee: S に含まれる辺の本数の期待値
ee = 0
for u in range(1, N + 1):
    for v in g[u]:
        if v == parent[u]:
            continue
        # 辺 (u, v) をぶった斬ることについて考える。
        x = size[v]  # v 側の頂点数
        y = N - size[v]  # u 側の頂点数
        # v 側, u 側両側に黒く塗られた頂点が少なくとも 1 つずつあることが
        # 辺 (u, v) が S に含まれることと同値である。
        # なので、そのような確率を足し合わせることで、辺 (u, v) の ee への寄与
        # を計上できる。
        ee += ((1 - inv_pow2[x]) * (1 - inv_pow2[y])) % MOD

# ev: S に含まれる頂点数の期待値
# |V| = |E| + (1 if |V| >= 1 else 0)
# ここで、|V| が 0 である確率は、全ての頂点が白の場合であるので 2^-N
# したがって、|V| >= 1 である確率は余事象を考えて 1 - 2^-N
# 期待値にすると
# E[|V|] = E[|E|] + 1 - 2^-N
ev = (ee + 1 - inv_pow2[N]) % MOD

# 穴あき度 = |V| - (黒い頂点数)
# E[穴あき度] = E[|V|] - E[黒い頂点数]
# E[黒い頂点数] = N * 1/2
# 黒い頂点は必ず S に含まれるので、それぞれの頂点が黒くなる確率を足し合わせれば期待値になる。
ans = (ev - N * inv_pow2[1]) % MOD
print(ans)
