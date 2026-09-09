# >>> atcoder-stat >>>
# started_at  = 2026-09-09T09:23:10+09:00
# solved_at   = 2026-09-09T09:53:20+09:00
# duration_ms = 1810841
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import functools

MOD = 998244353


N, K = map(int, input().split())
S = input()


@functools.cache
def palindrome(s: int):
    for i in range(K // 2):
        j = K - 1 - i
        if (s >> i) & 1 != (s >> j) & 1:
            return False
    return True


# dp[i][s] := i 文字目までみて、最後の K-1 文字の状態が s である良い文字列の個数
M = 1 << (K - 1)
dp = [0] * M
dp[0] = 1

nexts = {"A": [0], "B": [1], "?": [0, 1]}
for i in range(N):
    ndp = [0] * M
    for k in range(M):
        if dp[k] == 0:
            continue

        for bit in nexts[S[i]]:
            nk = (k << 1) | bit
            if i >= K - 1 and palindrome(nk):
                continue
            ndp[nk % M] += dp[k]

    dp = [x % MOD for x in ndp]

print(sum(dp) % MOD)
