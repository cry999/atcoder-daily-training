N, M = map(int, input().split())
(*A,) = map(int, input().split())

if sum(A) < M:
    print("No")
else:
    print("Yes")
