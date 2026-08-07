# >>> atcoder-stat >>>
# started_at  = 2026-08-07T16:01:36+09:00
# solved_at   = 2026-08-07T16:43:29+09:00
# duration_ms = 2513297
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 2
# <<< atcoder-stat <<<
N, D = map(int, input().split())
(*A,) = map(int, input().split())

A.sort()

# num[a] = A に含まれる a の個数
num = [0] * (A[-1] + 1)
for a in A:
    num[a] += 1

if D == 0:
    print(sum(max(0, n - 1) for n in num))
    exit()

INF = 10**18
# ans[d] = A の部分列の内, D で割ったあまりが d となる要素の集合
# に対する最小操作回数
ans = [INF] * D
# dp[x] = ans で定義した A の部分列で x が含まれる部分列について、
# x までの処理を決定した時の最小操作奇数
dp = [INF] * (A[-1] + 1)

for n in range(A[-1] + 1):
    if n - D < 0:
        # 操作しない
        dp[n] = 0
    elif n - 2 * D < 0:
        # 自分を消すか、一つ前を消すか
        dp[n] = min(num[n], num[n - D])
    else:
        # 自分を消すか、自分を消さないか
        # 自分を消す場合は、n-D までの最小操作回数を利用できる
        # 自分を消さない場合は、n-D を消して、n-2D までの最小操作回数を利用できる
        dp[n] = min(num[n] + dp[n - D], num[n - D] + dp[n - 2 * D])

print(f"[DEBUG] {dp=}")

ans = 0
for d in range(D):
    if A[-1] - d < 0:
        break
    ans += dp[A[-1] - d]
print(ans)
