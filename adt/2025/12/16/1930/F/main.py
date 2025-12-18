N, M = map(int, input().split())
*A, = map(int, input().split())
*B, = map(int, input().split())

C = [-1]*(N+M)
ai, bi = 0, 0
AI, BI = [-1]*N, [-1]*M

k = 0
while ai < N and bi < M:
    if A[ai] < B[bi]:
        AI[ai] = k+1
        C[k] = A[ai]
        ai += 1
    else:
        BI[bi] = k+1
        C[k] = B[bi]
        bi += 1
    k += 1

while ai < N:
    AI[ai] = k+1
    C[k] = A[ai]
    ai += 1
    k += 1

while bi < M:
    BI[bi] = k+1
    C[k] = B[bi]
    bi += 1
    k += 1

print(*AI)
print(*BI)
