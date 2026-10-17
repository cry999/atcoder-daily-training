N = int(input())
S = input()

ans = 0
i = 0
while i < N:
    j = i
    while j < N and S[j] == "R":
        j += 1

    ans = max(ans, j - i)
    i = j + 1
print(ans)
