N, S = map(int, input().split())
A = list(map(int, input().split()))

# dp[i][j] := (i 番目のカードまでを利用して, j が作れるか, i 番目のカードを利用するか)
dp = [[(False, False)] * (S + 1) for _ in range(N + 1)]
dp[0][0] = (True, False)

for i in range(N):
    for j in range(S + 1):
        if dp[i][j][0]:
            dp[i+1][j] = (True, False)
        elif j - A[i] >= 0 and dp[i][j-A[i]][0]:
            dp[i+1][j] = (True, True)

if not dp[N][S][0]:
    print(-1)
else:
    s = S
    cards = []
    for i in range(N, 0, -1):
        if dp[i][s][1]:  # i 番目のカードを利用する場合
            s -= A[i-1]
            cards.insert(0, i)
        else:  # i 番目のカードを利用しない場合
            pass
    print(len(cards))
    print(*cards)
