# >>> atcoder-stat >>>
# started_at  = 2026-07-09T16:07:56+09:00
# solved_at   = 2026-07-09T16:12:18+09:00
# duration_ms = 262516
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
M = 10**5
primes = []
is_prime = [True] * (10**5 + 1)
is_prime[0] = is_prime[1] = False

for p in range(2, M + 1):
    if not is_prime[p]:
        continue
    primes.append(p)
    for pp in range(p * 2, M + 1, p):
        is_prime[pp] = False

like_2017 = [0] * (M + 1)
for p in primes:
    if is_prime[(p + 1) // 2]:
        like_2017[p] = 1

for i in range(1, M + 1):
    like_2017[i] += like_2017[i - 1]

Q = int(input())
for _ in range(Q):
    l, r = map(int, input().split())
    print(like_2017[r] - like_2017[l - 1])
