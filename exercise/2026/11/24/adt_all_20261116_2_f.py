# >>> atcoder-stat >>>
# started_at  = 2026-11-24T10:11:58+09:00
# solved_at   = 2026-11-24T10:17:24+09:00
# duration_ms = 326773
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, Q = map(int, input().split())
S = input()
prefix = [0] * (N + 1)
for i in range(N):
    prefix[i + 1] = prefix[i]
    if i > 0 and S[i - 1] == S[i]:
        prefix[i + 1] += 1

for _ in range(Q):
    l, r = map(int, input().split())
    ans = prefix[r] - prefix[l - 1]
    if l > 1 and S[l - 2] == S[l - 1]:
        ans -= 1
    print(ans)
