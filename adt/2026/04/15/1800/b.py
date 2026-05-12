N = int(input())
S = [input() for _ in range(N)]
X, Y = input().split()

if S[int(X) - 1] == Y:
    print("Yes")
else:
    print("No")
