# >>> atcoder-stat >>>
# started_at  = 2026-07-02T14:43:05+09:00
# solved_at   = 2026-07-02T14:53:20+09:00
# duration_ms = 615410
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<

from bisect import bisect_left
import sys

input = sys.stdin.readline

N = 10**5
primes = set()
is_prime = [True] * (N + 1)
is_prime[0] = is_prime[1] = False

for p in range(2, N + 1):
    if not is_prime[p]:
        continue
    primes.add(p)
    for pp in range(2 * p, N + 1, p):
        is_prime[pp] = False

like_2017 = []
for p in primes:
    if (p + 1) // 2 in primes:
        like_2017.append(p)
like_2017.sort()

Q = int(input())
for _ in range(Q):
    l, r = map(int, input().split())

    i = bisect_left(like_2017, l)
    j = bisect_left(like_2017, r)

    print(f"[DEBUG] {l=} {r=} {i=} {j=}")
    ans = j - i
    if j < len(like_2017) and like_2017[j] == r:
        ans += 1
    print(ans)
