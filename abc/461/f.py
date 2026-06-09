from math import isqrt

MOD = 998244353

N = int(input())

divs = []
for x in range(1, isqrt(N) + 1):
    if N % x:
        continue
    divs.append(x)
    if x == N // x:
        continue
    divs.append(N // x)
divs.sort()

idx = {d: i for i, d in enumerate(divs)}
K = len(divs)
# 数列の最大長。「数列の要素は相異なる」ということから、相異なる要素で
# 構成される数列を考えるが、長さ n で最小の積になる相異なる要素による数列は
# 1, 2, ..., n である。この積を考えると n! である。n! > 10^10 (N の最大値)
# となる最小の n は 14 であるのでそれを数列の最大長とする。
B = 14

# dp0[b][i] := b 個の相異なる約数を選び、咳が divs[i] になる選び方の個数
dp0 = [[0] * K for _ in range(B + 1)]
# dp1[b][i] := 上記のような選び方全てについてのスコアの総和
dp1 = [[0] * K for _ in range(B + 1)]

dp0[0][idx[1]] = 1

for div in divs:
    for b in range(B - 1, -1, -1):
        row0 = dp0[b]
        row1 = dp1[b]

        nxt0 = dp0[b + 1]
        nxt1 = dp1[b + 1]

        for prod in divs:
            # b 個の相異なる約数を選び、積が prod になる選び方の個数
            cnt = row0[idx[prod]]
            if not cnt:
                continue

            new_prod = prod * div
            if new_prod > N:
                break
            if N % new_prod != 0:
                continue

            ci = idx[prod]
            ni = idx[new_prod]

            nxt0[ni] += cnt
            nxt0[ni] %= MOD

            nxt1[ni] += row1[ci] + cnt * div
            nxt1[ni] %= MOD

ans = 0
fact = 1
for b in range(1, B + 1):
    fact *= b
    fact %= MOD

    ans += dp1[b][idx[N]] * fact
    ans %= MOD

print(ans)
