import sys

sys.setrecursionlimit(10**7)


MOD = 10**9 + 7


H, W, N = map(int, input().split())
walls = sorted(
    [tuple(map(int, input().split())) for _ in range(N)],
    reverse=True,
)


fact = [1] * (H + W + 1)
invfact = [1] * (H + W + 1)
for i in range(1, H + W + 1):
    fact[i] = fact[i - 1] * i % MOD
    invfact[i] = invfact[i - 1] * pow(i, MOD - 2, MOD) % MOD


def comb(n: int, k: int) -> int:
    if n < 0 or not (0 <= k <= n):
        return 0
    if k == 0 or k == n:
        return 1

    if n - k < k:
        k = n - k

    return fact[n] * invfact[k] * invfact[n - k] % MOD


ans = comb(H - 1 + W - 1, min(H - 1, W - 1))

# to_goal_dp[i]: 壁 i からゴールへの経路数。
to_goal_dp = [0] * N

for i in range(N):
    ri, ci = walls[i]
    # 壁からゴールへの経路数を数える。
    to_goal_dp[i] = comb(H - ri + W - ci, min(H - ri, W - ci))
    for j in range(i):
        # 壁 i が壁 j を通過する場合を引く。
        # 並び替えにより、壁 i からゴールに向かう途中にある壁は i より
        # index が小さいものだけ。(ri <= rj and ci <= cj)
        # また、壁 i からゴールに向かう経路数は常に他の壁を経由するものはのぞいているので、
        # 単純に引くだけで良い。
        rj, cj = walls[j]
        # ri <= rj は常に成り立つ。(sort したから)
        # ci > cj はありうる。
        # この場合は、壁 i から壁 j に向かう道もその逆もないのでスキップ
        if ci > cj:
            continue

        # 壁 i から壁 j に向かう経路数
        to_j = comb(rj - ri + cj - ci, min(rj - ri, cj - ci))
        to_goal_dp[i] -= to_j * to_goal_dp[j]
        to_goal_dp[i] %= MOD

    ans -= comb(ri - 1 + ci - 1, min(ri - 1, ci - 1)) * to_goal_dp[i]
    ans %= MOD

print(ans)
