# >>> atcoder-stat >>>
# started_at  = 2026-09-26T17:21:19+09:00
# solved_at   = 2026-09-26T18:34:07+09:00
# duration_ms = 4368166
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
from math import comb
import sys

input = sys.stdin.readline


MOD = 998244353


class UnionFind:
    def __init__(self, n: int):
        self.root = list(range(n))
        self.size = [1] * n

    def find(self, x: int):
        r = self.root[x]
        if r != x:
            self.root[x] = self.find(r)
        return self.root[x]

    def union(self, x: int, y: int):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx

        self.root[ry] = rx
        self.size[rx] += self.size[ry]
        return True

    def groups(self):
        return {n for n, r in enumerate(self.root) if r == n}


# 考察
# 1. 同じ箱に入らないといけないグループは UnionFind で見つける
# 2. 1 の結果から root と箱の関係に変換する
# 3. 空き箱なしは、空き箱を i 個以上にする、を i の降順に求めていけば良い
# 4. P(i) = 空き箱を i 個以上にする場合の数, Q(i) = 空き箱を i 個にする場合の数
# 5. Q(i) = nCi * (N-i)^g - P(i+1); P(i) = Q(i) + P(i+1)

N, K, M = map(int, input().split())

uf = UnionFind(K)
for _ in range(M):
    u, v = map(int, input().split())
    uf.union(u - 1, v - 1)
g = len(uf.groups())

inv = [0] * (N + 1)
inv[1] = 1
for i in range(2, N + 1):
    q, r = divmod(MOD, i)
    inv[i] = (-q * inv[r]) % MOD

comb = [1] * (N + 1)
for i in range(N):
    comb[i + 1] = comb[i] * (N - i) * inv[i + 1] % MOD


ans = 0
for i in range(N + 1):
    c = comb[i] * pow(N - i, g, MOD) % MOD
    if i % 2 == 0:
        ans += c
    else:
        ans -= c
    ans %= MOD

print(ans)
