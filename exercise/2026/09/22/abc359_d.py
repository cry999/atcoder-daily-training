# >>> atcoder-stat >>>
# started_at  = 2026-09-22T16:12:11+09:00
# solved_at   = 2026-09-22T16:19:34+09:00
# duration_ms = 443900
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, K = map(int, input().split())
S = input()

M = 1 << (K - 1)
MASK = M - 1
MOD = 998244353

dp = [0] * M
dp[0] = 1

nexts = {
    "A": [0],
    "B": [1],
    "?": [0, 1],
}


def is_palindrome(s: int):
    for i in range(K // 2):
        j = K - 1 - i
        if ((s >> i) & 1) != ((s >> j) & 1):
            return False
    return True


for i in range(N):
    ndp = [0] * M
    for s in range(M):
        if dp[s] == 0:
            continue

        for b in nexts[S[i]]:
            ns = (s << 1) | b
            if i >= K - 1 and is_palindrome(ns):
                continue
            ndp[ns & MASK] += dp[s]

    dp = [x % MOD for x in ndp]

print(sum(dp) % MOD)
