N, A, B = map(int, input().split())
P, Q, R, S = map(int, input().split())

for a in range(P, Q+1):
    for b in range(R, S+1):
        if b-B == a-A or b-B == -(a-A):
            print('#', end='')
        else:
            print('.', end='')
    print()
