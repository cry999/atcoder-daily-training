import sys

input = sys.stdin.readline
print = sys.stdout.write

N, M = map(int, input().split())
S = input()
T = input()

C = [0] * (N + 1)

for i in range(M):
    L, R = map(int, input().split())
    C[L - 1] += 1
    C[R] -= 1

for i in range(N):
    C[i + 1] += C[i]

ans = []
for i in range(N):
    ans.append(S[i] if C[i] % 2 == 0 else T[i])
ans.append("\n")
print("".join(ans))
