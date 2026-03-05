from math import isqrt

MOD = 998244353

N = int(input())

ans = N * (N + 1) // 2
ans %= MOD

# ans = N * (N + 1) // 2 - sum(1 <= b <= N, N // b)
# NOTE: sum(1 <= b <= N, N // b) の部分を効率的に求める。

sn = isqrt(N)

for k in range(sn):
    k += 1
    # 1. N // b = k を満たす b の個数 (n) を求めて k * n を計上する
    #   N // b = k
    #   <-> k <= N / b < k+1
    #   <-> N / (k+1) < b <= N / k
    # なので、n = N // k - N // (k+1)
    ans -= k * (N // k - max(N // (k + 1), sn))

    # 2. b = k の時の N // b を計上する。
    ans -= N // k

    ans %= MOD

print(ans)
