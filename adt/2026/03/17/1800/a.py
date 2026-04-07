N = int(input())
S = input()

ans = -1
for i in range(N - 2):
    if S[i : i + 3] == "ABC":
        ans = i + 1
        break
print(ans)
