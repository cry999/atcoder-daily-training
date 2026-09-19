N = int(input())
(*A,) = map(int, input().split())

top3 = [A[0], A[1], 0]
for i in range(2, N):
    x = A[i]
    for i in range(3):
        if top3[i] < x:
            x, top3[i] = top3[i], x
    print(top3[2])
