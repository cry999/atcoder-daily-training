N, M = map(int, input().split())
(*A,) = map(int, input().split())


won = [0] * (N + 1)
winner = 1
winner_votes = 0
for a in A:
    won[a] += 1
    if winner_votes < won[a]:
        winner = a
        winner_votes = won[a]
    elif winner_votes == won[a] and a < winner:
        winner = a

    print(winner)
