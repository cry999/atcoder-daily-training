import sys

input = sys.stdin.readline


N, S = map(int, input().split())

# dp[i][s] := i 番目までのカードに書かれている数の和で s を実現する方法
dp = [[False] * (S + 1) for _ in range(N + 1)]
dp[0][0] = True

# cards[s] := s を実現するためのカードの表示
cards = [[""] * (S + 1) for _ in range(N + 1)]

for i in range(N):
    a, b = map(int, input().split())
    for s in range(S + 1):
        if s + a > S and s + b > S:
            break
        if not dp[i][s]:
            continue
        if s + a <= S:
            dp[i + 1][s + a] = dp[i][s]
            cards[i + 1][s + a] = cards[i][s] + "H"
        if s + b <= S:
            dp[i + 1][s + b] = dp[i][s]
            cards[i + 1][s + b] = cards[i][s] + "T"

if dp[N][S]:
    print("Yes")
    print("".join(cards[N][S]))
else:
    print("No")
