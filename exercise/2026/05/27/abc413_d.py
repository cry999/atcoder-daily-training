T = int(input())

for _ in range(T):
    N = int(input())
    (*A,) = map(int, input().split())

    if all(abs(A[0]) == abs(a) for a in A):
        pos = sum(a > 0 for a in A)
        neg = sum(a < 0 for a in A)
        if abs(pos - neg) == N % 2 or pos == neg or pos == 0 or neg == 0:
            print("Yes")
        else:
            print("No")
        continue

    A.sort(key=lambda x: abs(x))

    for i in range(N - 2):
        if A[i + 1] * A[i + 1] != A[i] * A[i + 2]:
            print("No")
            break
    else:
        print("Yes")
