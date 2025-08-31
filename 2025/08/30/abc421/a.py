N = int(input())
S = list(input() for _ in range(N))
X, Y = input().split()
X = int(X)

if Y == S[X-1]:
    print('Yes')
else:
    print('No')
