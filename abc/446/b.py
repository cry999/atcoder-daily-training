N, M = map(int, input().split())

drunk = [False] * (M + 1)

for _ in range(N):
    L = int(input())
    (*X,) = map(int, input().split())

    for x in X:
        if drunk[x]:
            continue
        drunk[x] = True
        print(x)
        break
    else:
        print(0)
