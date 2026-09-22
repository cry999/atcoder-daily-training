# >>> atcoder-stat >>>
# started_at  = 2026-09-21T21:28:14+09:00
# solved_at   = 2026-09-21T21:43:23+09:00
# duration_ms = 909631
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import math

N, M, K = map(int, input().split())
X, Y = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

A.sort()
B.sort()

# 購入する B の個数で尺取法。
# 1. Y が大きいので、B に利用できる K ドル札の枚数では DP できない。
# 2. B の個数自体で探索

prefix_sum_a = [0] * (N + 1)
for i in range(N):
    prefix_sum_a[i + 1] = prefix_sum_a[i] + A[i]

# B を一つも買わない場合の A の購入数
num_a = 0
while num_a + 1 <= N and prefix_sum_a[num_a + 1] <= X + K * Y:
    num_a += 1

ans = num_a
use_for_b = 0  # B の購入に使う K どる紙幣の枚数
change = 0  # B の購入に際して得たお釣り
for num_b in range(1, M + 1):
    # 次の B を購入するために必要な K どる紙幣の枚数
    n = math.ceil(B[num_b - 1] / K)
    if use_for_b + n > Y:
        break
    use_for_b += n
    change += K * n - B[num_b - 1]

    use_for_a = Y - use_for_b
    while num_a >= 0 and prefix_sum_a[num_a] > X + K * use_for_a + change:
        num_a -= 1

    ans = max(ans, num_a + num_b)
print(ans)
