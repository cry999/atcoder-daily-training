N = int(input())
S = input()
T = input()

for i in range(N):
    if S[i] == T[i] or T[i] == "*":
        continue
    print("No")
    break
else:
    print("Yes")
