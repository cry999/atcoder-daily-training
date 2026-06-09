N = int(input())
S = [input() for _ in range(N)]

unique = set(S[i] + S[j] for i in range(N) for j in range(N) if i != j)

print(len(unique))
