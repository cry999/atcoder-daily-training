# >>> atcoder-stat >>>
# started_at  = 2026-10-03T13:35:38+09:00
# solved_at   = 2026-10-03T14:18:04+09:00
# duration_ms = 2546715
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


MOD = 998244353


N, M = map(int, input().split())
friends = [set() for _ in range(2 * N + 1)]
for _ in range(M):
    a, b = map(int, input().split())
    friends[a - 1].add(b - 1)

fact = [1] * (2 * N + 1)
inv = [1] * (2 * N + 1)
inv_fact = [1] * (2 * N + 1)

for i in range(2, 2 * N + 1):
    fact[i] = fact[i - 1] * i % MOD
    q, r = divmod(MOD, i)
    inv[i] = -q * inv[r] % MOD
    inv_fact[i] = inv_fact[i - 1] * inv[i] % MOD


def comb(n: int, r: int):
    if n < r or r < 0:
        return 0

    return fact[n] * inv_fact[r] * inv_fact[n - r] % MOD


# 考察
# 1. dp[l][r] := 区間 [l, r) をペアを作って消す方法の数
# 2. ペアの作り方と、操作の順番で考える
# 3. ペアの作り方だけを考える時、l と k がペアになるとすると
# 4. A: 区間 [l+1, k) をペアを作って消す -> l と k をペアにして消す
# 5. B: 区間 [k+1, r) をペアを作って消す。
# 6. 順番について考えると、A と B は前後してもいい。その中身もどんな順番でもいい。
#    すなわち、A と B の順番を一つ決めた時、その実行方法は comb(na + nb, na) となる。
# 7. また、A は [l+1, k) を作ってから l と k を消す、という順番がある。
# 8. よって、dp[l][r] = dp[l+1][k] * dp[k+1][r] * comb(na + nb, na)
#    na = (k-l+1) // 2, nb = (r-k-1) // 2

dp = [[0] * (2 * N + 1) for _ in range(2 * N + 1)]
for i in range(2 * N + 1):
    dp[i][i] = 1

for d in range(2, 2 * N + 1, 2):
    for l in range(2 * N - d + 1):
        r = l + d
        for k in range(l + 1, r):
            if k not in friends[l]:
                continue
            na = (k - l + 1) // 2
            nb = (r - k - 1) // 2
            dp[l][r] += dp[l + 1][k] * dp[k + 1][r] * comb(na + nb, na)
            dp[l][r] %= MOD

print(dp[0][2 * N] % MOD)
