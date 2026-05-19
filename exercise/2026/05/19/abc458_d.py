from sortedcontainers import SortedList

X = int(input())
Q = int(input())

board = SortedList([X])

for i in range(Q):
    a, b = map(int, input().split())
    board.add(a)
    board.add(b)

    print(board[i + 1])
