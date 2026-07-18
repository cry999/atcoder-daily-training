# >>> atcoder-stat >>>
# started_at  = 2026-07-17T18:55:43+09:00
# solved_at   = 2026-07-17T19:00:44+09:00
# duration_ms = 301599
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
S = [0] * 10
for c in input():
    S[ord(c) - ord("0")] += 1

ans = 0
for i in range(10**7):
    d = i**2
    cnt = [0] * 10
    for _ in range(N):
        cnt[d % 10] += 1
        d //= 10
    if d > 0:
        break

    ans += cnt == S

print(ans)
