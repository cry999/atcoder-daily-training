from collections import Counter

N = int(input())
S = input()

count = Counter(S)

ans = count["R"] * count["G"] * count["B"]
for i in range(N):
    for d in range(1, min(i, N - i - 1) + 1):
        if len({S[i - d], S[i], S[i + d]}) != 3:
            continue
        ans -= S[i - d] != S[i + d]

print(ans)
