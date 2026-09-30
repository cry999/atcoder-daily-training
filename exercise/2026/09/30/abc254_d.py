# >>> atcoder-stat >>>
# started_at  = 2026-09-30T08:56:59+09:00
# solved_at   = 2026-09-30T09:10:13+09:00
# duration_ms = 794060
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
# 1. i x j = 平方数となる i, j の性質
# 2. i が 1 以外の平方数を含まない場合、j は i と等しいか、i x 平方数の形をしている。
# 3. i が平方数を含む場合、i' := i // (i が含む平方数) とすると、 2 と同じことが言える。
# 4. 逆に, j 側から見た時、j からあらかじめ平方数をのぞいておけば、i から平方数をのぞいた数と等しくなる。
# 5. 以上より、i, j から平方数をのぞいた数 f(i) を調べて、f(i) の等しい組み合わせを考えれば良い。
# 6. f(i) はどう求めるか?
# 7. i の含む平方数は高々 N^2 で O(N) で求められる。

# f[i] := i が含む最大の平方数
f = [1] * (N + 1)
for i in range(2, N + 1):
    i2 = i * i
    for k in range(1, N // i2 + 1):
        f[i2 * k] = i2
print(f"[DEBUG] {f=}")
counter = defaultdict(int)
for i in range(1, N + 1):
    counter[i // f[i]] += 1

ans = 0
for k, v in counter.items():
    if k == 0:
        continue
    ans += v * v
    print(f"[DEBUG] {k=} {v=}")
print(ans)
