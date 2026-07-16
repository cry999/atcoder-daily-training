N = int(input())
(*X,) = map(int, input().split())

for i in range(N):
    if X[i] >= 0:
        print("No")
        break
else:
    print("Yes")
