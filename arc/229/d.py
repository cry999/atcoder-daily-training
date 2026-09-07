T = int(input())

for _ in range(T):
    K = int(input())
    (*A,) = map(int, input().split())

    if all(a > K for a in A):
        print("Alice")
    else:
        print("Bob")
