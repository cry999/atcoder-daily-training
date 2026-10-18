N, M = map(int, input().split())
(*A,) = map(int, input().split())

S = sum(A)

dp = [0] * (1 << N)
memo = [0] * (1 << N)  # 各部分集合の総和 x M % S

for s in range(1, 1 << N):
    bit = s & -s
    prev = s ^ bit
    i = bit.bit_length() - 1

    memo[s] = (memo[prev] + A[i] * M % S) % S

    v = dp[prev]
    while prev:
        bit = prev & -prev
        v = max(v, dp[s ^ bit])
        prev ^= bit

    dp[s] = v + (memo[s] == 0)

print(M - dp[-1])
