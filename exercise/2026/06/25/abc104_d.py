MOD = 10**9 + 7
S = input()

A = 0
AB = 1
ABC = 2
dp = [0] * 3
pow3 = 1

for c in S:
    if c == "A":
        dp[A] += pow3
    elif c == "B":
        dp[AB] += dp[A]
    elif c == "C":
        dp[ABC] += dp[AB]
    else:  # c == '?'
        dp[ABC] = 3 * dp[ABC] + dp[AB]  # ? -> C
        dp[AB] = 3 * dp[AB] + dp[A]  # ? -> B
        dp[A] = 3 * dp[A] + pow3  # ? -> A
        pow3 *= 3
        pow3 %= MOD

    dp[A] %= MOD
    dp[AB] %= MOD
    dp[ABC] %= MOD

    print(f"[DEBUG] {c=} {dp=}")

print(dp[ABC])
