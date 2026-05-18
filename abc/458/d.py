from sortedcontainers import SortedList

X = int(input())
Q = int(input())

board = SortedList([X])

for i in range(Q):
    A, B = map(int, input().split())
    board.add(A)
    board.add(B)

    print(board[i + 1])
