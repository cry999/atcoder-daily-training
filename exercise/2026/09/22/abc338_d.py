# >>> atcoder-stat >>>
# started_at  = 2026-09-22T18:15:10+09:00
# solved_at   = 2026-09-22T18:30:21+09:00
# duration_ms = 911087
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N, M = map(int, input().split())
(*X,) = map(int, input().split())

# 考察
# 1. X[i] -> X[i+1] の移動は 2 通り。
# 1.1. 時計回りに X[i], X[i]+1, ..., X[i+1] と訪れる。 => abs(X[i+1] - X[i]) がコスト
# 1.2. 反時計回りに X[i], X[i]-1, ..., X[i+1] と訪れる => N-1-abs(X[i+1]-X[i]) がコスト
# 2. このコストの選択は、どの島を消すかで 1 通りに決まる
# 3. pre[i] を島 i を消す時の移動コストとしよう。

# pre[i] := 島 i と i+1 を繋ぐ端を消す時のコスト
pre = [0] * N
for i in range(M - 1):
    x1, x2 = sorted([X[i] - 1, X[i + 1] - 1])
    print(f"[DEBUG] {x1=}, {x2=}")
    # x1 -> x2 の移動を行うのは、[x1, x2] 間以外の端を消した場合
    pre[0] += x2 - x1
    pre[x1] -= x2 - x1
    pre[x2] += x2 - x1
    # x2 -> x1 の移動を行うのは、[x1, x2] 間の橋を消した場合
    pre[x1] += N - (x2 - x1)
    pre[x2] -= N - (x2 - x1)

    print(f"[DEBUG] {pre=}")

for i in range(N - 1):
    pre[i + 1] += pre[i]

print(min(pre))
