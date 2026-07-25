# >>> atcoder-stat >>>
# started_at  = 2026-07-23T12:54:19+09:00
# solved_at   = 2026-07-23T12:59:50+09:00
# duration_ms = 331191
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
S = input()

# dp[hand] := 最後に hand を出した時の勝った回数の最大値
dp = [0] * 3

hand = {
    "R": [0, 2],
    "S": [1, 0],
    "P": [2, 1],
}

for c in S:
    ndp = [0] * 3
    draw, win = hand[c]

    ndp[draw] = max(dp[h] for h in range(3) if h != draw)
    ndp[win] = max(dp[h] for h in range(3) if h != win) + 1

    dp = ndp

print(max(dp))
