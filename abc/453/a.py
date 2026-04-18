N = int(input())
S = input()

cur = 0
while cur < len(S) and S[cur] == "o":
    cur += 1
print(S[cur:])
