# >>> atcoder-stat >>>
# started_at  = 2026-07-19T10:16:13+09:00
# solved_at   = 2026-07-19T10:56:22+09:00
# duration_ms = 2409825
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys

sys.setrecursionlimit(10**7)

MOD = 10**9 + 7
N = int(input())
g = [[] for _ in range(N)]
for _ in range(N - 1):
    a, b = map(int, input().split())
    a, b = a - 1, b - 1
    g[a].append(b)
    g[b].append(a)

inv2 = pow(2, MOD - 2, MOD)
inv_pow2 = [1] * (N + 1)
for i in range(N):
    inv_pow2[i + 1] = (inv_pow2[i] * inv2) % MOD


def dfs(u: int, p: int = -1):
    node_num = 0
    exp = 0
    for v in g[u]:
        if v == p:
            continue
        xe, ee = dfs(v, u)
        exp = (ee + exp + (1 - inv_pow2[xe]) * (1 - inv_pow2[N - xe])) % MOD
        node_num += xe
    return node_num + 1, exp


# ee: S に含まれる辺の期待値
_, ee = dfs(0)
# es: S のサイズの期待値
es = (ee + 1 - inv_pow2[N]) % MOD
ans = (es - N * inv2) % MOD

print(ans)
