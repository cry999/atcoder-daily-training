N = int(input())
(*A,) = map(int, input().split())

B = [A[i] for i in range(N)]
op2 = [0] * N
op3 = [0] * N
for i in range(N):
    while B[i] % 2 == 0:
        B[i] //= 2
        op2[i] += 1
    while B[i] % 3 == 0:
        B[i] //= 3
        op3[i] += 1

if any(B[i] != B[0] for i in range(N)):
    print(-1)
else:
    n2 = min(op2)
    n3 = min(op3)

    print(sum(op2) - n2 * N + sum(op3) - n3 * N)
