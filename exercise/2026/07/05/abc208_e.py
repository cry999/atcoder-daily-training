# >>> atcoder-stat >>>
# started_at  = 2026-07-05T11:37:55+09:00
# solved_at   = 2026-07-05T11:37:58+09:00
# duration_ms = 1800000
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 2
# complexity  = 2
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
from collections import defaultdict

N, K = input().split()
(*N,) = map(int, N)
L = len(N)
K = int(K)

dp = [[[defaultdict(int) for _ in range(2)] for _ in range(2)] for _ in range(L + 1)]
dp[0][0][0][1] = 1

for i in range(L):
    n = N[i]
    for less in range(2):
        for started in range(2):
            for prod, cnt in dp[i][less][started].items():
                if cnt == 0:
                    continue

                stop = 9 if less else n
                for d in range(stop + 1):
                    nless = less or d < n
                    if not started and d == 0:
                        # まだ始まらない
                        nstarted = 0
                        nprod = 1
                    else:
                        nstarted = 1
                        nprod = min(K + 1, prod * d)

                    dp[i + 1][nless][nstarted][nprod] += cnt

ans = 0
for less in range(2):
    for prod, cnt in dp[L][less][True].items():
        if prod <= K:
            ans += cnt
print(ans)
