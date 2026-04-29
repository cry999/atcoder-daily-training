N, X, Y = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

dp = [float("inf")] * (1 << N)
dp[0] = 0


def f(s: int, x: int) -> int:
    """1 ~ N の内 s の bit が立っている数字を使った上で、残りの数字で x より小さいものの個数"""
    ans = 0
    for i in range(x):
        if s & (1 << i):
            continue
        ans += 1
    return ans


for nxt in range(1, 1 << N):
    n = nxt.bit_count() - 1
    for i in range(N):
        prv = nxt ^ (1 << i)
        dp[nxt] = min(dp[nxt], dp[prv] + abs(A[i] - B[n]) * X + f(prv, i) * Y)

print(dp[(1 << N) - 1])
