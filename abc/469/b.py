N = int(input())
S = input()

ans = 0
for i in range(N):
    if i > 0 and S[i - 1] == "o":
        continue
    if i + 1 < N and S[i + 1] == "o":
        continue
    ans += S[i] == "x"
print(ans)
