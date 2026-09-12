# >>> atcoder-stat >>>
# started_at  = 2026-09-10T10:27:03+09:00
# solved_at   = 2026-09-10T10:34:00+09:00
# duration_ms = 417663
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import functools

MOD = 998244353

N, K = map(int, input().split())
S = input()


@functools.cache
def palindrome(s: int):
    for i in range(K // 2):
        j = K - i - 1
        if (s >> i) & 1 != (s >> j) & 1:
            return False
    return True


M = 1 << (K - 1)

# dp[i][s] := i 文字目までみて、末尾の K-1 文字の状態が s である良い文字列の個数
dp = [0] * M
dp[0] = 1

next_bits = {"A": [1], "B": [0], "?": [0, 1]}

for i in range(N):
    ndp = [0] * M
    for s in range(M):
        for bit in next_bits[S[i]]:
            ns = (s << 1) | bit
            if i < K - 1 or not palindrome(ns):
                ndp[ns % M] += dp[s]
    dp[:] = [x % MOD for x in ndp]

print(sum(dp) % MOD)
