N, M = map(int, input().split())
S = input()
T = input()

cum = [0] * (N + 1)

for i in range(M):
    L, R = map(int, input().split())
    cum[L - 1] += 1
    cum[R] -= 1

for i in range(N):
    cum[i + 1] += cum[i]

ans = ''.join(S[i] if cum[i] % 2 == 0 else T[i] for i in range(N))

print(ans)
