N = int(input())
S = input()

ROCK, SCISSORS, PAPER = 0, 1, 2
# dp[i][j]: i 番目に手 j を出した時の最大勝利数
dp = [0] * 3

for i, aoki_hand in enumerate(S):
    if aoki_hand == 'R':
        win, draw, lose = PAPER, ROCK, SCISSORS
    elif aoki_hand == 'S':
        win, draw, lose = ROCK, SCISSORS, PAPER
    else:  # 'P'
        win, draw, lose = SCISSORS, PAPER, ROCK

    dp[win], dp[draw], dp[lose] = \
        max(dp[lose], dp[draw])+1, max(dp[win], dp[lose]), 0

print(max(dp))
