N = int(input())
S = [input() for _ in range(N)]

for i in range(N):
    for j in range(N):
        # 斜め向き(右下)
        if i + 5 < N and j + 5 < N:
            dots_cnt = 0
            for d in range(6):
                dots_cnt += S[i + d][j + d] == "."
            if dots_cnt <= 2:
                print("Yes")
                exit()
        # 斜め向き(左下)
        if i + 5 < N and j + 5 < N:
            dots_cnt = 0
            for d in range(6):
                dots_cnt += S[i + d][j + 5 - d] == "."
            if dots_cnt <= 2:
                print("Yes")
                exit()
        # 横向き
        if j + 5 < N:
            dots_cnt = 0
            for d in range(6):
                dots_cnt += S[i][j + d] == "."
            if dots_cnt <= 2:
                print("Yes")
                exit()
        # 縦向き
        if i + 5 < N:
            dots_cnt = 0
            for d in range(6):
                dots_cnt += S[i + d][j] == "."
            if dots_cnt <= 2:
                print("Yes")
                exit()
print("No")
