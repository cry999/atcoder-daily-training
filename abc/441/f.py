N, M = map(int, input().split())
goods = [tuple(map(int, input().split())) for _ in range(N)]

dp_forward = [[0] * (M + 1) for _ in range(N + 1)]
dp = dp_forward
dp[0][0] = 0
for i in range(N):
    p, v = goods[i]
    for m in range(M + 1):
        dp[i + 1][m] = dp[i][m]
        if 0 <= m - p:
            dp_forward[i + 1][m] = max(dp[i + 1][m], dp[i][m - p] + v)

dp_backward = [[0] * (M + 1) for _ in range(N + 1)]
dp = dp_backward
dp[N][0] = 0
for i in range(N - 1, -1, -1):
    p, v = goods[i]
    for m in range(M + 1):
        dp[i][m] = dp[i + 1][m]
        if 0 <= m - p:
            dp[i][m] = max(dp[i][m], dp[i + 1][m - p] + v)

max_value = max(dp_forward[N])
ans = ""
for i in range(N):
    p, v = goods[i]
    is_optional = False  # なくても条件を達成できる
    can_select = False  # 選んでも条件を達成できる
    for j in range(M + 1):
        if M - j >= 0 and dp_forward[i][j] + dp_backward[i + 1][M - j] == max_value:
            is_optional = True
        if (
            M - p - j >= 0
            and dp_forward[i][j] + dp_backward[i + 1][M - p - j] == max_value - v
        ):
            can_select = True
    if is_optional and can_select:
        ans += "B"
    elif is_optional:
        ans += "C"
    else:
        ans += "A"
print(ans)
