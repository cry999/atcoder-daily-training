while True:
    H = int(input())
    if H == 0:
        break

    board = [[] for _ in range(5)]
    for _ in range(H):
        (*row,) = map(int, input().split())
        for i in range(5):
            board[i].append(row[i])
    for i in range(5):
        board[i].reverse()

    score = 0
    tobe_continued = True
    while tobe_continued:
        for i in range(H):
            for j in range(5):
                if len(board[j]) <= i:
                    continue
                c = board[j][i]
                d = 0
                while j + d < 5 and i < len(board[j + d]) and board[j + d][i] == c:
                    d += 1
                if d >= 3:
                    d = 0
                    while j + d < 5 and i < len(board[j + d]) and board[j + d][i] == c:
                        score += board[j + d][i]
                        board[j + d][i] = 0
                        d += 1

        next_board = [[] for _ in range(5)]
        tobe_continued = False
        for j in range(5):
            for n in board[j]:
                if n == 0:
                    tobe_continued = True
                    continue
                next_board[j].append(n)
        board = next_board
        # print("[DEBUG] ===")
        # for row in board:
        #     print(f"[DEBUG]   {row}")

    print(score)
