MOD = 10000
N = int(input())

bb = 0
for _ in range(N):
    T, A = input().split()
    A = int(A)
    if T == '+':
        bb += A
    elif T == '-':
        bb -= A
    elif T == '*':
        bb *= A
    bb %= MOD
    print(bb)
