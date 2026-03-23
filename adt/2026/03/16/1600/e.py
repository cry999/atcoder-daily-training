from itertools import permutations

N, M = map(int, input().split())
S = [input() for _ in range(N)]

ans = "No"
for perm in permutations(range(N)):
    for i in range(N - 1):
        j, k = perm[i], perm[i + 1]
        tj, tk = S[j], S[k]
        if 1 != sum(1 for a, b in zip(tj, tk) if a != b):
            break
    else:
        ans = "Yes"
        break
print(ans)
