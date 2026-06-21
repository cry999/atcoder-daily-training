N, X = input().split()
N = int(N)
X = ord(X) - ord("A")

for _ in range(N):
    S = input()
    if S[X] == "o":
        print("Yes")
        break
else:
    print("No")
