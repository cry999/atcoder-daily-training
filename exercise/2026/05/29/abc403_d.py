N, D = map(int, input().split())
(*A,) = map(int, input().split())

MAX_A = max(A)

if D == 0:
    # D = 0 の時は、同じ数を一つになるまで消す。
    print(N - len(set(A)))
    exit()

count = [0] * (MAX_A + 1)
dp = [float("inf")] * (MAX_A + 1)

for a in A:
    count[a] += 1

for a in range(min(D, MAX_A + 1)):
    dp[a] = 0
    prev = count[a]
    while a + D <= MAX_A:
        a += D
        dp[a] = min(dp[a], prev)
        prev = dp[a - D] + count[a]
        dp[a] = min(dp[a], prev)


ans = 0
for i in range(D):
    if MAX_A - i < 0:
        break
    ans += dp[MAX_A - i]
print(ans)
