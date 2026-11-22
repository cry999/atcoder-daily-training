import sys

N, M = map(int, input().split())
S = [input() for _ in range(N)]

for i in range(N):
    if S[i].count("x") == M:
        print("Faucet", i + 1)
        sys.exit()
    if S[i].count("x") == 1:
        j = S[i].index("x")
        print("Drain", j + 1)
        sys.exit()
