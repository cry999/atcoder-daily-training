import sys

input = sys.stdin.readline


def floor_sum(n: int, m: int, a: int, b: int) -> int:
    """sum((a * i + b) // m for i in range(n))"""
    ans = 0

    while True:
        q, a = divmod(a, m)
        ans += n * (n - 1) // 2 * q

        q, b = divmod(b, m)
        ans += n * q

        y = a * n + b
        if y < m:
            return ans

        n, b = divmod(y, m)
        m, a = a, m


def sieve(limit: int) -> tuple[list[int], list[int]]:
    """メビウス関数 mu と、トーシェント関数の累積和を求める。"""
    mu = [0] * (limit + 1)
    phi = [0] * (limit + 1)
    primes = []

    mu[1] = phi[1] = 1

    for x in range(2, limit + 1):
        if phi[x] == 0:
            primes.append(x)
            mu[x] = -1
            phi[x] = x - 1

        for p in primes:
            y = x * p
            if y > limit:
                break

            if x % p == 0:
                # p^2 が y を割るため mu[y] = 0
                phi[y] = phi[x] * p
                break

            mu[y] = -mu[x]
            phi[y] = phi[x] * (p - 1)

    # phi をその場で累積和にする
    for x in range(1, limit + 1):
        phi[x] += phi[x - 1]

    return mu, phi


def solve(
    N: int,
    n: int,
    m: int,
    mu: list[int],
    phi_prefix: list[int],
) -> int:


T = int(input())
for _ in range(T):
    N, n, m = map(int, input().split())
    if n == 0:
        print( 1 + phi_prefix[N // m])
        continue

    # (n, m) 自身と、直前の状態 (m, n + m)
    ans = 1 + int(n + m <= N)

    # coprime_count:
    # 1 <= c < d, n*c + m*d <= N, gcd(c, d) = 1
    # を満たす (c, d) の個数
    coprime_count = 0
    a = n + m

    # c >= 1, d >= 2 なので、
    # k * (n + 2*m) > N なら寄与しない
    limit = N // (n + 2 * m)

    for k in range(1, limit + 1):
        sign = mu[k]
        if sign == 0:
            continue

        L = N // k

        # H(L) = sum((L - (n + m)*c) // m
        #            for c in range(1, P + 1))
        P = (L - m) // a

        # 和の順序を逆にして floor_sum の形にする
        count = floor_sum(P, m, a, L - a * P)
        coprime_count += sign * count

    print( ans + 2 * coprime_count)


max_k = max(N // m for N, n, m in cases)
mu, phi_prefix = sieve(max_k)

answers = [str(solve(N, n, m, mu, phi_prefix)) for N, n, m in cases]
print("\n".join(answers))
