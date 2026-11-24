# >>> atcoder-stat >>>
# started_at  = 2026-11-24T14:10:48+09:00
# <<< atcoder-stat <<<
N, L = map(int, input().split())
(*A,) = map(int, input().split())

# dp[x][y][l] := 場に残っている種類 x, 既知の種類 y, ライフ残り l の時の獲得できる種類数の期待値
dp = [[[0.0] * (L + 1) for _ in range(N + 1)] for _ in range(N + 1)]

for x in range(1, N + 1):
    for l in range(1, L + 1):
        for y in range(x + 1):
            # 1. 1 枚目に既知のカードの相方をひく
            m = 2 * x - y
            if y > 0:  # 既知のカードがあること
                p = y / m
                dp[x][y][l] += (1 + dp[x - 1][y - 1][l]) * p

            # 2. 1 枚目に片方がわかっていないカードをひく
            if x - y >= 1:  # 未知のカードが 1 枚以上残っていること
                p = 2 * (x - y) / m

                # 2.1 1 枚目と同じカードをひく
                q = 1 / (m - 1)
                dp[x][y][l] += (1 + dp[x - 1][y][l]) * p * q

                # 2.2 1 枚目と違うカードで、片方がわかっているカードをひく
                if y > 0:  # 既知のカードがあること
                    q = y / (m - 1)
                    if l > 1:
                        # ライフが残っている場合は、次のターンに 2 枚目のペアをとる
                        dp[x][y][l] += (1 + dp[x - 1][y][l - 1]) * p * q
                    else:
                        # ライフが残っていない場合は、次のターンに取れない
                        dp[x][y][l] += dp[x][y + 1][l - 1] * p * q

                # 2.3 1 枚目と違うカードで、片方がわかっていないカードをひく
                if x - y >= 2 and y + 2 <= N:  # 未知のカードが 2 枚以上残っていること
                    q = (m - 1 - y - 1) / (m - 1)
                    dp[x][y][l] += dp[x][y + 2][l - 1] * p * q

print(dp[N][0][L] * sum(A) / N)
