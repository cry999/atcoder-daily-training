T = int(input())

for _ in range(T):
    N = int(input())
    (*A,) = map(int, input().split())

    A.sort(key=lambda x: abs(x))

    if all(abs(A[i]) == abs(A[0]) for i in range(N)):
        if abs(A.count(-A[0]) - A.count(A[0])) == N % 2:
            print("Yes")
        elif A.count(A[0]) == 0 or A.count(-A[0]) == 0:
            print("Yes")
        else:
            print("No")
    else:
        for i in range(1, N - 1):
            if A[i] * A[i] != A[i + 1] * A[i - 1]:
                print("No")
                break
        else:
            print("Yes")
