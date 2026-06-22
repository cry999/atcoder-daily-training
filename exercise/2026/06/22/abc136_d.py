S = input()
N = len(S)

ans = [0] * N

i = 0
while i < N:
    j = i
    while j < N and S[j] == "R":
        j += 1

    ans[j] += (j - i) // 2
    ans[j - 1] += (j - i) // 2 + (j - i) % 2

    i = j + 1
    while i < N and S[i] == "L":
        i += 1

i = N - 1
while i >= 0:
    j = i
    while j >= 0 and S[j] == "L":
        j -= 1

    ans[j] += (i - j) // 2
    ans[j + 1] += (i - j) // 2 + (i - j) % 2

    i = j - 1
    while i >= 0 and S[i] == "R":
        i -= 1

print(*ans)
