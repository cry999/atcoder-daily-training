# >>> atcoder-stat >>>
# started_at  = 2026-09-05T05:07:42+09:00
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*X,) = map(int, input().split())

# diff[i] := 橋 i を壊した時の移動距離
# 橋 i := i と (i+1) mod N の間の橋
diff = [0] * (N + 1)
for i in range(1, M):
    x1, x2 = sorted([X[i], X[i - 1]])

    r1 = x2 - x1
    r2 = N - r1

    # X[i] と X[i-1] の間の橋を壊せば r2 の距離を移動する必要があり、
    # そこ以外を壊せば r1 の距離を移動することになる。

    # x1 と x2 の間の橋を壊す場合
    diff[x1 - 1] += r2
    diff[x2 - 1] -= r2
    # それ以外の橋を壊す場合
    diff[0] += r1
    diff[x1 - 1] -= r1
    diff[x2 - 1] += r1
    diff[N] -= r1

for i in range(1, N):
    diff[i] += diff[i - 1]

print(min(diff[:N]))
