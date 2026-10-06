# >>> atcoder-stat >>>
# started_at  = 2026-10-02T13:29:35+09:00
# solved_at   = 2026-10-02T14:05:55+09:00
# duration_ms = 2180567
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 3
# impl        = 1
# verify      = 3
# <<< atcoder-stat <<<
import functools
import sys

input = sys.stdin.readline


MOD = 998244353

N, M = map(int, input().split())
friends = [[] for _ in range(2 * N)]
for _ in range(M):
    a, b = map(int, input().split())
    friends[a - 1].append(b - 1)
for f in friends:
    f.sort()

# dp[l][r] := 区間 [l, r) を消す方法の数
dp = [[0] * (2 * N + 1) for _ in range(2 * N + 1)]
for i in range(2 * N + 1):
    dp[i][i] = 1

inv = [0] * (2 * N + 1)
inv[1] = 1
for i in range(2, 2 * N + 1):
    q, r = divmod(MOD, i)
    inv[i] = -q * inv[r] % MOD


@functools.cache
def comb(n: int, r: int):
    if r == n or r == 0:
        return 1
    return comb(n - 1, r - 1) * n * inv[r] % MOD


for d in range(2, 2 * N + 1, 2):
    for l in range(2 * N - d + 1):
        r = l + d
        for k in friends[l]:
            if r <= k:
                break
            if (k - l) % 2 == 0:
                continue
            # l と k をペアにして消す方法を考える
            # A: l と k の間の [l+1, k) を消した後に l-k のペアを消す
            # -> 順番含めて dp[l+1][k] 通り
            # B: k の右側の [k+1, r) を消す
            # -> 順番含めて dp[k+1][r] 通り
            # A と B は独立なので、それぞれの中で行われる操作の順番は
            # comb(a + b, a) 通りある。
            # ただし、
            # a := A の操作回数 = (k - l + 1) // 2
            # b := B の操作回数 = (r - k - 1) // 2
            a = (k - l + 1) // 2
            b = (r - k - 1) // 2
            dp[l][r] += dp[l + 1][k] * dp[k + 1][r] * comb(a + b, a) % MOD
            dp[l][r] %= MOD

print(dp[0][2 * N])
