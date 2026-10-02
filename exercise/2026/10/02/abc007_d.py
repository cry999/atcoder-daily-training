# >>> atcoder-stat >>>
# started_at  = 2026-10-02T08:57:17+09:00
# solved_at   = 2026-10-02T09:13:23+09:00
# duration_ms = 966450
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
A, B = map(int, input().split())

# 考察
# 1. f(X) = X 以下の禁止されていない数字の個数
#   (多分、禁止されていない数字の方が求めやすい)
# 2. 1 により、答えは (B - (A-1)) - (f(B) - f(A-1)) となる。
# 3. 桁 DP の典型が思い出せない... less を使うんだよな...
# 4. 最上位桁から決めていって、X 以下が確定した時点で less = true にするんだったな。


def f(n: str):
    x = str(n)
    dp = [[0] * 2 for _ in range(len(x) + 1)]
    dp[0][0] = 1
    for i in range(len(x)):
        s = int(x[i])
        for less in range(2):
            limit = 9 if less else s
            for d in range(limit + 1):
                if d == 4 or d == 9:
                    continue
                nless = less or d < s
                dp[i + 1][nless] += dp[i][less]

    return sum(dp[len(x)])


ans = (B - f(B)) - (A - 1 - f(A - 1))
print(ans)
