MOD = 998244353

N, K = map(int, input().split())
S = list(input())


def is_palindrome(n: int) -> bool:
    u = 1 << (K - 1)
    l = 1
    for _ in range(K // 2):
        if (n & u == 0) != (n & l == 0):
            return False
        u >>= 1
        l <<= 1
    return True


def usable(bit: int, i: int):
    for j, c in enumerate(reversed(S[i : i + K])):
        if c == "A" and bit & (1 << j) == 0:
            return False
        elif c == "B" and bit & (1 << j) != 0:
            return False
    return True


ONE = 1 << (K - 1)
ZERO = 0
dp = [[0] * (1 << (K - 1)) for _ in range(N - K + 2)]
for bit in range(1 << (K - 1)):
    dp[0][bit] = 1

for i in range(N - K + 1):
    for bit in range(1 << (K - 1)):
        if S[i] in "A?" and usable(bit | ONE, i):
            if not is_palindrome(bit | ONE):
                dp[i + 1][bit] += dp[i][(bit | ONE) >> 1]
        if S[i] in "B?" and usable(bit | ZERO, i):
            if not is_palindrome(bit | ZERO):
                dp[i + 1][bit] += dp[i][(bit | ZERO) >> 1]
        dp[i + 1][bit] %= MOD

print(sum(dp[N - K + 1]) % MOD)
