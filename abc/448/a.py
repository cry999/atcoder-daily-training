N, X = map(int, input().split())
(*A,) = map(int, input().split())
for a in A:
    if a < X:
        X = a
        print(1)
    else:
        print(0)
