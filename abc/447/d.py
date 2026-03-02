S = input()
i = j = k = len(S) - 1

op = 0
while i >= 0 and j >= 0 and k >= 0:
    while k >= 0 and S[k] != "C":
        k -= 1
    j = min(j, k - 1)
    while j >= 0 and S[j] != "B":
        j -= 1
    i = min(i, j - 1)
    while i >= 0 and S[i] != "A":
        i -= 1

    if i >= 0 and j >= 0 and k >= 0:
        op += 1

    i, j, k = i - 1, j - 1, k - 1

print(op)
