# >>> atcoder-stat >>>
# started_at  = 2026-10-03T11:35:41+09:00
# solved_at   = 2026-10-03T11:41:21+09:00
# duration_ms = 340817
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
from collections import defaultdict

N = int(input())

# 考察
# 1. i x j が平方数。i が平方数を含むかどうかで場合分け
# 2. i が平方数を含まない場合、j は i x (平方数) の形をしている
# 3. i が平方数を含む場合、その最大の平方数を f(i) とすると j は i / f(i) x (平方数) という形をしている
# 4. j 側の平方数も f(j) で表すと、i / f(i) = j / f(j) となる
# 5. i / f(i) = j / f(j) を満たす (i, j) の組を数え上げれば良い。

f = [1] * (N + 1)
for i in range(2, N + 1):
    i2 = i * i
    for j in range(i2, N + 1, i2):
        f[j] = i2

count = defaultdict(int)
for i in range(1, N + 1):
    count[i // f[i]] += 1

ans = sum(v * v for v in count.values())
print(ans)
