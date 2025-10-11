N = int(input())
A = [list(map(int, input().split())) for _ in range(N)]
lines = [i for i in range(N)]


def debug_print():
    print('---')
    for i in range(N):
        print([A[lines[i]][lines[j]] for j in range(N)])
    print()


Q = int(input())
for _ in range(Q):
    c, x, y = map(int, input().split())
    # print('Query:', c, x, y)
    if c == 1:  # swap lines
        lines[x-1], lines[y-1] = lines[y-1], lines[x-1]
    else:  # print
        print(A[lines[x-1]][y-1])
    # debug_print()
