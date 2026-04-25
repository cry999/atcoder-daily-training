N = int(input())
S = input()

fab = {0: 1}
fbc = {0: 1}
fca = {0: 1}
fabc = {(0, 0): 1}

A = [0] * (N + 1)
B = [0] * (N + 1)
C = [0] * (N + 1)

for i in range(N):
    A[i + 1] = A[i] + (S[i] == "A")
    B[i + 1] = B[i] + (S[i] == "B")
    C[i + 1] = C[i] + (S[i] == "C")

    fab[A[i + 1] - B[i + 1]] = fab.get(A[i + 1] - B[i + 1], 0) + 1
    fbc[B[i + 1] - C[i + 1]] = fbc.get(B[i + 1] - C[i + 1], 0) + 1
    fca[C[i + 1] - A[i + 1]] = fca.get(C[i + 1] - A[i + 1], 0) + 1
    fabc[(A[i + 1] - B[i + 1], A[i + 1] - C[i + 1])] = (
        fabc.get((A[i + 1] - B[i + 1], A[i + 1] - C[i + 1]), 0) + 1
    )

nab = sum(v * (v - 1) // 2 for v in fab.values())
nbc = sum(v * (v - 1) // 2 for v in fbc.values())
nca = sum(v * (v - 1) // 2 for v in fca.values())
nabc = sum(v * (v - 1) // 2 for v in fabc.values())
ans = N * (N + 1) // 2 - nab - nbc - nca + 2 * nabc
print(ans)
