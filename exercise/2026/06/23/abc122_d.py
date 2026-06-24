MOD = 10**9 + 7
N = int(input())

T = 0
A = 1
G = 2
C = 3
dp = [[0] * (4 * 4 * 4) for _ in range(N + 1)]
dp[0][0] = 1

for i in range(N):
    for p in range(4 * 4 * 4):
        pp, p3 = divmod(p, 4)
        p1, p2 = divmod(pp, 4)
        for n in range(4):
            if p2 == A and p3 == G and n == C:
                continue
            if p2 == G and p3 == A and n == C:
                continue
            if p2 == A and p3 == C and n == G:
                continue
            if p1 == A and p2 == G and n == C:
                continue
            if p1 == A and p3 == G and n == C:
                continue

            nn = (p2 * 4 + p3) * 4 + n
            dp[i + 1][nn] += dp[i][p]
            dp[i + 1][nn] %= MOD

print(sum(dp[N]) % MOD)
# print(dp)
