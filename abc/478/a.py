N, M = map(int, input().split())
q, r = divmod(M, N)
for i in range(N):
    if i < r:
        print(q + 1)
    else:
        print(q)
