N = int(input())
S = input()

MOD = 998244353

divs = [d for d in range(1, N) if N % d == 0]
patterns = [0] * N

for M in divs:
    patterns[M] = 1
    for j in range(M):
        while j < N:
            if S[j] == ".":
                break
            j += M
        else:
            patterns[M] *= 2
            patterns[M] %= MOD

# print(patterns)
for M in divs:
    a = M + M
    while a < N:
        patterns[a] -= patterns[M]
        patterns[a] %= MOD
        a += M

# print(patterns)
ans = sum(patterns[M] for M in divs) % MOD
print(ans)
