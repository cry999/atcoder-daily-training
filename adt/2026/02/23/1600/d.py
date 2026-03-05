N = int(input())
(*A,) = map(int, input().split())
P = 0

board = [[0] * 4 for _ in range(2)]

for i in range(N):
    for j in range(4):
        board[1 - (i & 1)][j] = 0
    board[i & 1][0] += 1

    for j in range(4):
        if j + A[i] < 4:
            board[1 - (i & 1)][j + A[i]] += board[i & 1][j]
        else:
            P += board[i & 1][j]

print(P)
