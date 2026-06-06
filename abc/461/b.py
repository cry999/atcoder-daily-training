N = int(input())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

for i in range(N):
    if i + 1 == B[A[i] - 1]:
        continue
    print("No")
    break
else:
    print("Yes")
