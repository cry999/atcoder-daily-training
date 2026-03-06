S = input()
N = len(S)

ans = 0
for i in range(N):
    if S[i] != "A":
        continue

    for j in range(i + 1, N):
        if S[j] != "B":
            continue

        k = j + (j - i)
        if k >= N:
            break
        if S[k] != "C":
            continue

        ans += 1

print(ans)
