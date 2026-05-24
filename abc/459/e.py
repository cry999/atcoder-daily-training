import sys

sys.setrecursionlimit(10**7)

MOD = 998244353

N = int(input())
(*P,) = map(int, input().split())
(*C,) = map(int, input().split())
(*D,) = map(int, input().split())

g = [[] for _ in range(N)]

for i in range(N - 1):
    g[P[i] - 1].append(i + 1)


max_d = max(D)
inv = [0] * (max_d + 1)
if max_d >= 1:
    inv[1] = 1
for i in range(2, max_d + 1):
    inv[i] = MOD - (MOD // i) * inv[MOD % i] % MOD


def comb(n: int, k: int) -> int:
    if k < 0 or n < k:
        return 0

    if n >= MOD:
        n -= MOD

    if k > n:
        return 0

    ret = 1
    for i in range(1, k + 1):
        ret = ret * (n - i + 1) % MOD
        ret = ret * inv[i] % MOD

    return ret


ans = 1


def dfs(u: int):
    global ans

    n = C[u]
    for v in g[u]:
        n += dfs(v)
    # print(f"dfs({u=}): {n=}")
    ans *= comb(n, D[u])
    ans %= MOD
    return max(n - D[u], 0)


dfs(0)
print(ans)
